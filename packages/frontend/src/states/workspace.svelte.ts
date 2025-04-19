
import { backendDisconnectWorkspace, backendReadAllUvDependencies, backendSaveWorkspace } from "$services/backend.svelte"
import { parse, stringify } from "smol-toml"
import { gstore, } from "./global.svelte"
import { tick } from "svelte"

import { qoslabappGetCliWs } from "$services/qoslabapp.svelte"

import { Equipments } from "./equipment.svelte"
import { Experiments } from "./experiment.svelte"
import { Dependencies, sourceEqual, type DependencyT } from "./dependency.svelte"

import { readTextFile, readDir, writeTextFile, exists, mkdir } from "@tauri-apps/plugin-fs"
import { retryOnError, shell } from "./utils.svelte"
import { confirm, message } from "@tauri-apps/plugin-dialog"
import { Child, Command } from "@tauri-apps/plugin-shell"
import type { EET, EEType } from "./ee.svelte"
import { applicationError } from "./err"


export type Save = {
    dependencies: DependencyT[] | undefined,
    experiments: EET[],
    equipments: EET[],
}

export class Workspace {
    private _path: string = $state("")
    get path() {
        return this._path
    }

    private log_socket: WebSocket | undefined = $state()
    private _connected: boolean = $state(false)
    get connected() {
        return this._connected
    }

    private _dependencies: Dependencies | undefined = $state(undefined)
    get dependencies() {
        return this._dependencies
    }


    private _equipments: Equipments = $state(new Equipments())
    get equipments() {
        return this._equipments
    }
    private _experiments: Experiments = $state(new Experiments())
    get experiments() {
        return this._experiments
    }

    private proc: Child | undefined


    save = async () => {
        await backendSaveWorkspace({
            path: this._path,
            save: {
                dependencies: this._dependencies ? this._dependencies.toSave() : undefined,
                equipments: this._equipments.toSave(),
                experiments: this._experiments.toSave(),
            }
        })
    }

    reset = () => {
        this._dependencies = undefined
        this._equipments = new Equipments()
        this._experiments = new Experiments()
    }


    disconnect = async () => {
        this._connected = false
        await tick();
        // shutdown the workspace
        try {
            await backendDisconnectWorkspace()
            this.reset()
            await tick();
        } catch (e) {
            this._connected = true;
            throw e
        }
    }



    connect = async (path: string) => {
        this._path = path

        await tick()
        const dir = await readDir(path)



        // STEP 1 setup uv

        // Check if the workspace has pyproject.toml
        if (!await exists(path + "/pyproject.toml")) {
            if (dir.length > 0) {
                // Not empty directory without pyproject.toml
                const confirmation = await confirm(
                    `${path} is not empty. Are you sure to create setup workspace here?`,
                    { title: 'Directory Not Empty', kind: 'warning' }
                );

                // Abort if user chooses not to
                if (!confirmation) return
            }

            // Run uv init 
            shell({ fn: "uv", cmd: "init", cwd: this._path })
        }

        // Write link-mode to suppress error
        const parsed = parse(await readTextFile(path + "/pyproject.toml"));
        parsed.tool = { uv: { "link-mode": "copy" } }
        await writeTextFile(path + "/pyproject.toml", stringify(parsed))

        // STEP 2: setup gitignore

        // Read gitignore if exists
        let gitignore_content: string[] = []
        if (await exists(path + "/.gitignore"))
            gitignore_content = (await readTextFile(path + "/.gitignore")).split("\n")

        // Put beinn into list of gitignores
        if (!gitignore_content.includes("meall"))
            await writeTextFile(path + "/.gitignore", [...gitignore_content, "meall"].join("\n"))


        // STEP 3: use copier to copy newest meall into the directory
        await shell({ fn: "uvx", cmd: "copier copy git+https://github.com/qosUoG/Beinn.git ./meall -f", cwd: path })

        // STEP 4: Create the data directory if not exist
        if (!await exists(path + "/data"))
            await mkdir(path + "/data")

        // STEP 5: install required dependencies
        await shell({ fn: "uv", cmd: "add fastapi fastapi[standard] aiosqlite", cwd: path })
        await shell({ fn: "uv", cmd: "add git+https://github.com/qosUoG/Beinn#subdirectory=packages/cnoc --branch main", cwd: path })

        // In case cnoc is already installed and stale
        await shell({ fn: "uv", cmd: "lock --upgrade-package cnoc", cwd: path })

        // STEP 5: Execute meall as a child process
        const handler = Command.create(
            "uv", "run uvicorn meall.main:app --host localhost --port 8000".split(" "), {
            encoding: "utf8",
            cwd: path
        })
        handler.stdout.on("data", async (message) => {
            await gstore.logs.push([
                { source: "python", timestamp: Date.now(), content: message }
            ])
        })
        handler.stderr.on("data", async (message) => {
            await gstore.logs.push([
                { source: "python", timestamp: Date.now(), content: message }
            ])
        })

        this.proc = await handler.spawn()

        // STEP 6: Wait until the beinn is online with 5 seconds timeout
        await retryOnError(5000, async () => {
            const res = await (await fetch("http://localhost:8000/workspace/status")).json();
            if (res.status !== "online")
                throw Error()
        });

        const res = await (await fetch("http://localhost:8000/workspace/status")).json();
        if (res.status !== "online")
            await message("Timeout trying to start meall. meall is not online", { title: "meall startup timeout", "kind": "error" })

        // STEP 7: try to get the save
        if (!await exists(path + "/.beinn"))
            return

        const save: Save = JSON.parse(await readTextFile(path + "/.beinn"))

        // 2. Connect to cli ws
        this.log_socket = qoslabappGetCliWs<string>({
            onmessage: (message) => {
                const res = JSON.parse(message.data) as
                    | {
                        type: "exec";
                        result: null;
                    }
                    | { type: "eval"; result: string }
                    | {
                        type: "error";
                        result: string;
                    };

                if (res.type !== "exec")
                    gstore.logs.push([{
                        source: "equipment",
                        timestamp: Date.now(),
                        content: res.result,
                    }]);
            },
        });


        // 3. Instantiate the dependencies

        // First prepare the dependencies already installed in qoslabapp
        const uv_dependencies = await backendReadAllUvDependencies({ path: gstore.workspace.path })

        // If there is no save, just load the dependencies and update availables is enough.
        if (!save) {

            this._dependencies = new Dependencies(uv_dependencies)
            await Promise.all([this._equipments.refreshAvailables(), this._experiments.refreshAvailables()])
            this._connected = true;
            return
        }

        // Otherwise, we would need to loop through the save and add one by one
        this._dependencies = new Dependencies()

        if (save.dependencies)
            for (const save_d of save.dependencies) {
                // Just in case for the nested $state to update
                await tick()

                // First check if the source is present in pyproject.toml already
                if (uv_dependencies.find(({ source }) => sourceEqual(save_d.source, source))) {
                    // Just add the dependency
                    this._dependencies.instantiateTemplate(save_d)
                    continue
                }

                // The source is not present in pyproject.toml
                // Check if the dependency is installed. If not, just copy as is
                if (!save_d.installed) {
                    this._dependencies.instantiateTemplate(save_d)
                    continue
                }

                // The dependency should be installed, but not. Try to install.
                // First assigne the source
                const new_d = this._dependencies.instantiate()
                new_d.source = save_d.source
                await tick()

                // Then try to install
                try { await new_d.install() }
                catch (e) { /* If it failed, we silence the error, and only show that as not installed */ }
            }

        await tick()
        await Promise.all([this._equipments.refreshAvailables(), this._experiments.refreshAvailables()])
        await tick();



        // Instantiate all equipments and experiments
        const new_equipments = save.equipments.map((e) => this._equipments.instantiate(e))
        const new_experiments = save.experiments.map((e) => this._experiments.instantiate(e))

        await tick()




        // Write the module_cls to the equipment and experiments
        for (let i = 0; i < save.equipments.length; i++) {

            new_equipments[i].module_cls = save.equipments[i].module_cls
            await tick()

            // If not created, this is enough
            if (!save.equipments[i].created) continue

            // If it is created, try to create it
            await new_equipments[i].create()

        }

        for (let i = 0; i < save.experiments.length; i++) {
            new_experiments[i].module_cls = save.experiments[i].module_cls
            await tick()
            // If not created, this is enough
            if (!save.experiments[i].created) continue

            // If it is created, try to create it
            await new_experiments[i].create()
        }
        await tick()

        // First set the params to temp_params, and try to save it, then write the temp_params 
        for (let i = 0; i < save.equipments.length; i++) {
            new_equipments[i].temp_params = save.equipments[i].params
            await tick()

            // Set the params
            await new_equipments[i].saveParams()

            await tick()

            // Then overwrite the temp_params
            new_equipments[i].temp_params = save.equipments[i].temp_params

            await tick()

        }

        for (let i = 0; i < save.experiments.length; i++) {
            new_experiments[i].temp_params = save.experiments[i].params

            await tick()



            // Set the params
            await new_experiments[i].saveParams()

            await tick()

            // Then overwrite the temp_params
            new_experiments[i].temp_params = save.experiments[i].temp_params

            await tick()
        }

        this._connected = true;

        await tick();
    }

    async sendCommand(input: string) {
        // Check if cli websocket is connected
        if (this.log_socket === undefined) throw applicationError("Websocket to qoslabapp for cli is undefined");
        let sent = false

        // Get the inputs
        let inputs: string[]
        if (input.includes("."))
            inputs = input.split(".")
        else inputs = [input]

        // Check if any input in inputs is the experiment
        const equipment_name = inputs[0];

        for (const equipment of Object.values(this._equipments.equipments)) {
            if (!equipment.created) continue

            if (equipment.name === equipment_name) {
                // Reconstruct the command and send to python
                this.log_socket.send(
                    JSON.stringify({
                        type: "equipment",
                        id: equipment.id,
                        command: input.slice(equipment_name.length),
                    })
                );
                sent = true
                break
            }
        }

        if (!sent)
            this.log_socket.send(
                JSON.stringify({
                    type: "general",
                    command: input,
                })
            );

        // Record the command into the log
        await gstore.logs.push([{
            source: "equipment",
            timestamp: Date.now(),
            content: input,
        }]);

        gstore.command_history.push(input);


    }

    getEEs(eetype: EEType) {
        if (eetype === "equipment") return this._equipments
        return this._experiments
    }

    getEEsList(eetype: EEType) {
        if (eetype === "equipment") return this._equipments.equipments
        return this._experiments.experiments
    }

    getEE(eetype: EEType, id: string) {
        if (eetype === "equipment") return this._equipments.equipments[id]
        return this._experiments.experiments[id]
    }



}


