
import { exists, readDir, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"
import { parse, stringify } from "smol-toml"
import { dependency_controller } from "./DependencyController.svelte"
import { tick } from "svelte"
import { confirm } from "@tauri-apps/plugin-dialog"
import { shell, sleep } from "$lib/utils"
import { Child, Command } from "@tauri-apps/plugin-shell"

import { beinn_log_controller } from "./LogController.svelte"
import { cnoc_controller } from "./CnocController.svelte"


const ws_url = "ws://localhost:8001/"

class WorkspaceController {

    workspace_ws: WebSocket | null = null
    connected: boolean = $state(false)
    path: string | null = $state(null)

    private uvproc: Child | undefined

    constructor() {
        this.workspace_ws = new WebSocket(ws_url + "close")

    }

    #commands: Record<string, (obj: any) => Promise<void> | void> = {}
    #onopen: (() => void)[] = []
    /* 
    Connect to the python workspace
    */
    async connect(path: string) {

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

        beinn_log_controller.append("Install required dependency_controller")

        let success = true
        success = (await shell({ fn: "uv", cmd: "add git+https://github.com/qosUoG/Beinn#subdirectory=packages/cnoc --branch revert_threading", cwd: path, logger: beinn_log_controller })).success

        if (!success) {
            beinn_log_controller.append("FAILED connect to python")
            return
        }

        success = (await shell({ fn: "uv", cmd: "sync", cwd: path, logger: beinn_log_controller })).success
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
        beinn_log_controller.append("Start python as a child process")
        const handler = Command.create(
            "uv", "run cnoc".split(" "), {
            encoding: "utf8",
            cwd: path
        })
        handler.stdout.on("data", (message) => { cnoc_controller.append(message) })
        handler.stderr.on("data", (message) => { cnoc_controller.append(message) })

        this.uvproc = await handler.spawn()
        if (this.uvproc === undefined) {
            beinn_log_controller.append("FAILED connect to python: uv process is undefined")
            return
        }

        // Get dependency_controller
        await dependency_controller.get_dependencies({ path })

        await sleep(2000) // Wait for uv to start


        // Connect to the websocket

        this.workspace_ws = new WebSocket(ws_url + "workspace")

        this.workspace_ws.onmessage = async (event: MessageEvent<string>) => {
            const data = JSON.parse(event.data)
            await this.#commands[data.command](data.value)
        }

        this.workspace_ws.onopen = () => {
            this.#onopen.forEach((cb) => cb())
            this.connected = true
        }

        this.workspace_ws.onclose = () => {
            console.log("Workspace WebSocket closed")
            this.connected = false
        }

        beinn_log_controller.append("END connect to python")

    }

    registerOnOpen(cb: () => void) {
        this.#onopen.push(cb)
    }

    registerCallback(command: string, handler: (obj: any) => Promise<void> | void) {
        this.#commands[command] = handler
    }

    sendCommand(command: string, data: any) {
        if (this.workspace_ws === null || this.workspace_ws.readyState !== WebSocket.OPEN) {
            beinn_log_controller.append(`FAILED send command ${command}: workspace is not connected`)
            return
        }
        this.workspace_ws.send(JSON.stringify({ command, value: data }))
    }


}

export const workspace_controller = $state(new WorkspaceController())