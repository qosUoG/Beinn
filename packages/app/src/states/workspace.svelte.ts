

import { parse, stringify } from "smol-toml"

import { tick } from "svelte"

import { meallGetCliWs, meallGetPid_throwable, meallWaitUntilOnline } from "$lib/meall.svelte"

import { Equipment, Equipments } from "./equipment.svelte"
import { Experiment, Experiments } from "./experiment.svelte"
import { Dependencies, sourceEqual, type DependencyT } from "./dependency.svelte"

import { readTextFile, readDir, writeTextFile, exists, mkdir } from "@tauri-apps/plugin-fs"

import { confirm } from "@tauri-apps/plugin-dialog"
import { Child, Command } from "@tauri-apps/plugin-shell"
import type { EET, EEType } from "./ee.svelte"
import { beginProcedure, readAllUvDependencies, shell } from "$lib/utils"
import { platform } from '@tauri-apps/plugin-os';
import { pushLog } from "$components/modules/LogPanelController.svelte"
import { pushCli } from "$components/modules/CliPanelController.svelte"

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

    private _dependencies: Dependencies = $state(new Dependencies())
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

    private uvproc: Child | undefined
    private meall_pid: number | undefined

    async refreshAvailables_throwable() {
        await Promise.all([this._equipments.refreshAvailables_throwable(), this._experiments.refreshAvailables_throwable()])
    }

    async save() {

        const { step, completed, unhandled } = await beginProcedure("SAVE WORKSPACE")

        try {
            await step(`Save workspace in ${this._path}/.beinn`,
                async () => {
                    const save: Save = {
                        dependencies: this._dependencies ? this._dependencies.toSave() : undefined,
                        equipments: this._equipments.toSave(),
                        experiments: this._experiments.toSave(),
                    }

                    await writeTextFile(this._path + "/.beinn", JSON.stringify(save))
                })
            await completed()
        } catch (e) {
            await unhandled(e)
        }
    }

    async reset() {
        this._dependencies = new Dependencies()
        this._equipments = new Equipments()
        this._experiments = new Experiments()
    }


    // TODO REDO CLEANUP
    async kill() {

        if (!this.uvproc) return


        const currentPlatform = platform();
        if (currentPlatform === "windows") {
            await shell({ fn: "taskkill", cmd: `/PID ${this.meall_pid} /F` })
            await shell({ fn: "taskkill", cmd: `/PID ${this.uvproc.pid} /F` })
        }
        else if (currentPlatform === "linux" || currentPlatform === "macos") {
            await shell({ fn: "kill", cmd: `-s SIGKILL ${this.meall_pid}` })
            await shell({ fn: "kill", cmd: `-s SIGKILL ${this.uvproc.pid}` })
        }



    }


    // TODO REDO CLI FEATURE
    connect = async (path: string) => {

        const { step, completed, cancelled, unhandled } = await beginProcedure("CONNECT MEALL")

        try {

            this._path = path
            await tick()


            const cont = await step("Setup uv in workspace",
                async () => {
                    if (await exists(path + "/pyproject.toml")) return true

                    if ((await readDir(path)).length > 0) {
                        // Not empty directory without pyproject.toml
                        const confirmation = await confirm(
                            `${path} is not empty. Are you sure to create setup workspace here?`,
                            { title: 'Directory Not Empty', kind: 'warning' }
                        );

                        // Abort if user chooses not to
                        if (!confirmation) {
                            await cancelled("user aborted connection")
                            return false
                        }
                    }

                    // Run uv init 
                    await shell({ fn: "uv", cmd: "init", cwd: this._path })
                    return true
                }

            )

            if (!cont) return

            await step("Upsert 'link-mode: copy' to pyproject.toml",
                async () => {
                    const parsed = parse(await readTextFile(path + "/pyproject.toml"));
                    if (parsed.tool === undefined) parsed.tool = {}
                    if (parsed.tool.uv === undefined) parsed.tool.uv = {}
                    if (parsed.tool.uv["link-mode"] === undefined) parsed.tool.uv["link-mode"] = "copy"

                    await writeTextFile(path + "/pyproject.toml", stringify(parsed))
                }
            )

            await step("Upsert 'meall' to .gitignore",
                async () => {
                    let gitignore_content: string[] = []
                    if (await exists(path + "/.gitignore"))
                        gitignore_content = (await readTextFile(path + "/.gitignore")).split("\n")

                    // Put meall into list of gitignores
                    if (!gitignore_content.includes("meall"))
                        await writeTextFile(path + "/.gitignore", [...gitignore_content, "meall"].join("\n"))
                }
            )

            // await step("Copy newest version of meall to workspace",
            //     async () => {
            //         await shell({ fn: "uvx", cmd: "copier copy -r main git+https://github.com/qosUoG/Beinn.git ./meall -f", cwd: path })
            //     }
            // )

            await step("Create data directory if not exist",
                async () => {
                    if (!await exists(path + "/data"))
                        await mkdir(path + "/data")
                }
            )

            await step("Install required dependencies",
                async () => {
                    await shell({ fn: "uv", cmd: "add git+https://github.com/qosUoG/Beinn#subdirectory=packages/cnoc --branch main", cwd: path })

                    await shell({ fn: "uv", cmd: "sync", cwd: path })
                    await shell({ fn: "uv", cmd: "add fastapi", cwd: path })
                    await shell({ fn: "uv", cmd: "add fastapi[standard]", cwd: path })
                    await shell({ fn: "uv", cmd: "add aiosqlite", cwd: path })

                    // In case cnoc is already installed and stale
                    await shell({ fn: "uv", cmd: "lock --upgrade-package cnoc", cwd: path })
                }
            )

            await step("Start meall as a child process",
                async () => {
                    const handler = Command.create(
                        "uv", "run uvicorn meall.main:app --host localhost --port 8000".split(" "), {
                        encoding: "utf8",
                        cwd: path
                    })
                    handler.stdout.on("data", async (message) => { await pushLog("meall", message) })
                    handler.stderr.on("data", async (message) => { await pushLog("meall", message) })

                    this.uvproc = await handler.spawn()
                }
            )

            await step("Wait until meall is online",
                async () => {
                    await meallWaitUntilOnline()
                }
            )

            await step("Get meall pid",
                async () => {
                    this.meall_pid = (await meallGetPid_throwable())
                })



            // TODO REDO CLI FEATURE
            await step("Setup websocket connection to meall for cli feature",
                async () => {
                    this.log_socket = meallGetCliWs<string>({
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
                                pushCli(res.result);
                        },
                    });
                })

            const uv_dependencies = await step("Fetch workspace dependencies from pyproject.toml",
                async () => {
                    return await readAllUvDependencies()
                }
            )


            const save = await step("Load workspace save .beinn if exist",
                async () => {
                    if (!await exists(path + "/.beinn")) {
                        this._dependencies = new Dependencies(uv_dependencies)
                        await tick()
                        await this.refreshAvailables_throwable()
                        this._connected = true;
                        return
                    }

                    return JSON.parse(await readTextFile(path + "/.beinn")) as Save
                })

            if (!save) {
                await completed()
                return
            }

            this._dependencies = new Dependencies()

            await tick()

            await step("Load save's dependencies into workspace",
                async () => {
                    if (!save.dependencies) return

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
                        // First assign the source
                        const new_d = this._dependencies.instantiate()
                        new_d.source = save_d.source
                        await tick()

                        // Then try to install
                        try { await new_d.install() }
                        catch (e) { /* If it failed, we silence the error, and only show that as not installed */ }

                        await tick()



                    }



                    // add uv dependencies that is installed but not present in save
                    for (const uv_d of uv_dependencies) {
                        // Just in case for the nested $state to update
                        await tick()

                        // First check if the source is present in pyproject.toml already
                        if (!save.dependencies.find(({ source }) => sourceEqual(uv_d.source, source))) {
                            // Just add the dependency
                            this._dependencies.instantiateTemplate(uv_d)


                        }

                    }

                    await tick()


                })

            await tick()



            await step("Refresh list of available equipment and experiment",
                async () => {
                    await tick()
                    await this.refreshAvailables_throwable()
                    await tick();
                })

            const new_equipments = await step("Instantiate all equipment according to save",
                async () => {
                    await tick()
                    const res: Equipment[] = []
                    for (const e of save.equipments)
                        res.push(await this._equipments.instantiate_throwable(step, e))
                    return res
                }
            )

            const new_experiments = await step("Instantiate all experiment according to save",
                async () => {
                    await tick()
                    const res: Experiment[] = []
                    for (const e of save.experiments)
                        res.push(await this._experiments.instantiate_throwable(step, e))
                    return res
                }
            )



            await step("Load Module and Class of Equipment and Experiment according to save",
                async () => {
                    await tick()
                    // Write the module_cls to the equipment and experiments
                    for (let i = 0; i < save.equipments.length; i++) {

                        new_equipments[i].module_cls_throwable = save.equipments[i].module_cls
                        await tick()

                        // If not created, this is enough
                        if (!save.equipments[i].created) continue

                        // If it is created, try to create it
                        await new_equipments[i].create()

                    }

                    for (let i = 0; i < save.experiments.length; i++) {
                        new_experiments[i].module_cls_throwable = save.experiments[i].module_cls
                        await tick()
                        // If not created, this is enough
                        if (!save.experiments[i].created) continue

                        // If it is created, try to create it
                        await new_experiments[i].create()
                    }

                    await tick()
                })

            await step("Try setting params according to save",
                async () => {
                    // First set the params to temp_params, and try to save it, then write the temp_params 
                    for (let i = 0; i < save.equipments.length; i++) {
                        new_equipments[i].temp_params_throwable = save.equipments[i].params
                        await tick()

                        // Set the params
                        await new_equipments[i].saveParams()

                        await tick()

                        // Then overwrite the temp_params
                        new_equipments[i].temp_params_throwable = save.equipments[i].temp_params

                        await tick()

                    }

                    for (let i = 0; i < save.experiments.length; i++) {
                        new_experiments[i].temp_params_throwable = save.experiments[i].params

                        await tick()



                        // Set the params
                        await new_experiments[i].saveParams()

                        await tick()

                        // Then overwrite the temp_params
                        new_experiments[i].temp_params_throwable = save.experiments[i].temp_params

                        await tick()
                    }
                }
            )

            this._connected = true;
            await tick();
        } catch (e) {
            await unhandled(e)
        }

    }

    // TODO REDO CLI FEATURE
    async sendCommand(input: string) {
        // Check if cli websocket is connected
        if (this.log_socket === undefined)
            // throw applicationError("Websocket to meall for cli is undefined");
            throw ""

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
        await pushCli(input)





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


export const workspace = $state(new Workspace())