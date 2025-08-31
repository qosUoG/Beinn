
import { exists, readDir, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"
import { parse, stringify } from "smol-toml"
import { dependency_controller } from "./dependency.svelte"
import { tick } from "svelte"
import { confirm } from "@tauri-apps/plugin-dialog"
import { cnoc_url, sleep } from "$lib/utils"
import { Child, Command } from "@tauri-apps/plugin-shell"

import { beinn_log_controller } from "./log.svelte"
import { cnoc_controller } from "./cnoc.svelte"
import { shell } from "$lib/svelte_utils"
import { equipment_controller } from "./equipment.svelte"
import { experiment_controller } from "./experiment.svelte"




class WorkspaceController {

    workspace_ws: WebSocket | null = null
    connection: "connecting" | "connected" | "disconnected" = $state("disconnected")
    save_status: "normal" | "success" | "fail" | "saving" = $state("normal")

    path: string | null = $state(null)

    #uvproc: Child | undefined

    constructor() {
        new WebSocket(cnoc_url + "close")
    }

    #commands: Record<string, ((value: any, id: string) => Promise<void> | void)[]> = {}
    #onopen: (() => void | Promise<void>)[] = []
    /* 
    Connect to the python workspace
    */
    async connect(path: string) {
        this.connection = "connecting"

        beinn_log_controller.append("BEGIN connect to python")

        // Update the path
        this.path = path
        await tick()


        beinn_log_controller.append(`Check if ${path} is a valid workspace...`)
        if (!await exists(path + "/pyproject.toml")) {
            // Check if the directory exists and is not empty
            if ((await readDir(path)).length > 0) {
                // Not empty directory without pyproject.toml
                const confirmation = await confirm(
                    `${path} is not empty. Are you sure to setup workspace here?`,
                    { title: 'Directory Not Empty', kind: 'warning' }
                );

                // Abort if user chooses not to
                if (!confirmation) {
                    beinn_log_controller.append("FAILED connect to python: user aborted")
                    return
                }
            }

            // Run uv init 
            beinn_log_controller.append("Running uv init...")
            const { success } = await shell({ fn: "uv", cmd: "init", cwd: path, logger: beinn_log_controller })
            if (!success) {
                beinn_log_controller.append("FAILED connect to python")
                return
            }
        }

        beinn_log_controller.append("Upsert 'link-mode: copy' to pyproject.toml")

        const parsed = parse(await readTextFile(path + "/pyproject.toml")) as any;
        if (parsed.tool === undefined) parsed.tool = {}
        if (parsed.tool.uv === undefined) parsed.tool.uv = {}
        if (parsed.tool.uv["link-mode"] === undefined) parsed.tool.uv["link-mode"] = "copy"
        await writeTextFile(path + "/pyproject.toml", stringify(parsed))

        beinn_log_controller.append("Install required dependencies")

        let success = true
        success = (await shell({ fn: "uv", cmd: "add pandas tables numpy", cwd: path, logger: beinn_log_controller })).success

        if (!success) {
            beinn_log_controller.append("FAILED connect to python")
            return
        }

        success = (await shell({ fn: "uv", cmd: "add git+https://github.com/qosUoG/Beinn#subdirectory=packages/cnoc", cwd: path, logger: beinn_log_controller })).success
        if (!success) {
            beinn_log_controller.append("FAILED connect to python")
            return
        }

        // In case cnoc is already installed and stale
        success = (await shell({ fn: "uv", cmd: "lock --upgrade-package cnoc", cwd: path, logger: beinn_log_controller })).success
        if (!success) {
            beinn_log_controller.append("FAILED connect to python")
            return
        }

        success = (await shell({ fn: "uv", cmd: "sync", cwd: path, logger: beinn_log_controller })).success
        if (!success) {
            beinn_log_controller.append("FAILED connect to python")
            return
        }

        beinn_log_controller.append("Start python as a child process")
        const handler = Command.create(
            "uv", "run cnoc".split(" "), {
            encoding: "utf8",
            cwd: path
        })
        handler.stdout.on("data", (message) => { cnoc_controller.append(message) })
        handler.stderr.on("data", (message) => { cnoc_controller.append(message) })

        this.#uvproc = await handler.spawn()
        if (this.#uvproc === undefined) {
            beinn_log_controller.append("FAILED connect to python: uv process is undefined")
            return
        }


        await dependency_controller.get_dependencies({ path })

        // Get save
        let save: any | undefined = undefined
        if (await exists(path + "/.beinn")) {

            beinn_log_controller.append("Try to load save from " + path + "/.beinn")
            save = JSON.parse(await readTextFile(path + "/.beinn"))
            dependency_controller.loadSave(save.dependencies)

        }

        await sleep(2000) // Wait for uv to start

        // Connect to the websocket
        this.workspace_ws = new WebSocket(cnoc_url + "workspace")

        this.workspace_ws.onmessage = async (event: MessageEvent<string>) => {
            const data = JSON.parse(event.data)
            console.log(data)

            for (const fn of this.#commands[data.command])
                if (fn) await fn(data.value, data.id)

        }

        this.workspace_ws.onopen = () => {
            this.#onopen.forEach(async (cb) => await cb())
            // Wait for 2 seconds to make sure the save is loaded
            setTimeout(() => {
                this.connection = "connected"
            }, 2000)

            setTimeout(async () => {
                if (save) {
                    await equipment_controller.loadSave(save.equipments)
                    await experiment_controller.loadSave(save.experiments)
                }

            })



        }

        this.workspace_ws.onclose = () => {
            console.log("Workspace WebSocket closed")

        }

        beinn_log_controller.append("END connect to python")

    }

    async disconnect() {
        if (this.workspace_ws === null) return
        this.connection = "connecting"
        await tick()
        this.sendCommand("kill", {})
        await sleep(1000)
        this.path = null
        cnoc_controller.reset()
        experiment_controller.reset()
        equipment_controller.reset()
        dependency_controller.reset()
        beinn_log_controller.reset()
        this.connection = "disconnected"
    }

    async kill() {
        if (this.workspace_ws === null) return

        for (const experiment of experiment_controller.instances_arr) {
            if (!experiment.status.endsWith("ing")) continue

            const should_kill = await confirm("Experiment might still be running. Are you sure to force kill the workspace?",
                { title: "Beinn", kind: "warning" })

            if (!should_kill) return false

            // send stop experiments command
            for (const experiment of experiment_controller.instances_arr) {
                if (!experiment.status.endsWith("ing")) continue
                experiment_controller.stop(experiment.name)
            }
            await sleep(1000)

            // Send kill command to workspace
            this.sendCommand("kill", {})
            await sleep(1000)
            break
        }

        // There are no running experiment
        this.workspace_ws.close()

        return true

    }

    registerOnOpen(cb: () => void) {
        this.#onopen.push(cb)
    }

    registerCallback(command: string, handler: (obj: any, request_id: string) => Promise<void> | void) {
        if (!(command in this.#commands)) this.#commands[command] = []
        this.#commands[command].push(handler)

        return async (callback: (() => Promise<void> | void) | undefined = undefined) => {
            this.#commands[command] = this.#commands[command].filter(fn => fn !== handler)
            if (callback) await callback()
        }
    }

    sendCommand(command: string, data: any) {
        if (this.workspace_ws === null || this.workspace_ws.readyState !== WebSocket.OPEN) {
            beinn_log_controller.append(`FAILED send command ${command}: workspace is not connection`)
            return
        }
        const id = crypto.randomUUID()
        console.log(data)
        console.log(JSON.stringify({ command, value: data, id }))
        this.workspace_ws.send(JSON.stringify({ command, value: data, id }))
        return id
    }

    async save() {
        this.save_status = "saving"
        const save_path = this.path + "/.beinn"
        const save = {
            dependencies: dependency_controller.getSave(),
            equipments: equipment_controller.getSave(),
            experiments: experiment_controller.getSave(),

        }
        beinn_log_controller.append(`BEGIN save workspace to ${save_path}`)

        try {
            await writeTextFile(save_path, JSON.stringify(save))
            beinn_log_controller.append(`END save workspace to ${save_path}`)
            this.save_status = "success"

        }
        catch (e) {
            beinn_log_controller.append(`FAILED save workspace to ${save_path}`)
            this.save_status = "fail"
        }

    }




}

export let workspace_controller = $state(new WorkspaceController())