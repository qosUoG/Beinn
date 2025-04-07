
import { backendDisconnectWorkspace, backendLoadWorkspace, backendReadAllUvDependencies, backendSaveWorkspace } from "$services/backend.svelte"

import { gstore, type Availables } from "./global.svelte"
import { tick } from "svelte"
import { getRandomId } from "$lib/utils"
import { qoslabappGetCliWs } from "$services/qoslabapp.svelte"

import { Equipments } from "./equipment.svelte"
import { Experiments } from "./experiment.svelte"
import { Dependencies } from "./dependency.svelte"
import { toastUnreacheable } from "$components/modules/ToastController.svelte"
import { applicationError, sourceEqual, userError, type EEType } from "qoslab-shared"



export class Workspace {
    readonly path: string = $state(import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH)

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


    save = async () => {
        await backendSaveWorkspace({
            path: this.path,
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



    connect = async () => {
        // 0. Check that the path is valid
        if (this.path === "") throw userError("project path shall not be empty")

        // 1. set the project directory and get the save
        const save = await backendLoadWorkspace({ path: this.path });

        console.log(save)

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
                const new_d = await this._dependencies.instantiate()
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
        const [new_equipments, new_experiments] = await Promise.all([
            Promise.all(save.equipments.map((e) => this._equipments.instantiate(e))),
            Promise.all(save.experiments.map((e) => this._experiments.instantiate(e)))
        ])


        console.log(this._equipments.available_module_cls)
        console.log(this._experiments.available_module_cls)

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

    sendCommand(input: string) {
        // Check if cli websocket is connected
        if (this.log_socket === undefined) throw applicationError("Websocket to qoslabapp for cli is undefined");
        let sent = false
        if (!input.includes(".")) {
            // Not targeting equipment, directly send command to python
            this.log_socket.send(
                JSON.stringify({
                    type: "general",
                    command: input,
                })
            );
            sent = true
        } else {
            // Targeting equipment, first check if the equipment name exist
            const equipment_name = input.split(".")[0];

            for (const equipment of Object.values(this._equipments)) {
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


        }

        if (sent) {
            // Record the command into the log
            gstore.logs.push([{
                source: "equipment",
                timestamp: Date.now(),
                content: input,
            }]);

        } else {
            gstore.logs.push([{
                source: "equipment",
                timestamp: Date.now(),
                content: `Command ${input} failed to interpret`
            }])
        }
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


