
import { exists, mkdir, readDir, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"
import { parse, stringify } from "smol-toml"
import type { Dependency, DependencySource, GitSource, PathSource } from "./dependency"
import { tick } from "svelte"
import { confirm, message } from "@tauri-apps/plugin-dialog"
import { beginProcedure, getRequestJsonOut_throwable, retryOnError, shell, sleep } from "$lib/utils"
import { Child, Command } from "@tauri-apps/plugin-shell"
import { pushLog } from "$components/modules/LogPanelController.svelte"

const ws_url = "ws://localhost:8001/"

class AppController {

    workspace_ws: WebSocket | null = null
    connected: boolean = $state(false)
    path: string | null = $state(null)
    dependencies: Dependency[] = $state([])
    private uvproc: Child | undefined

    constructor() {
        this.workspace_ws = new WebSocket(ws_url + "close")

    }


    /* 
    Connect to the python workspace
    */
    async connect(path: string) {

        const { step, completed, cancelled, unhandled } = await beginProcedure("CONNECT PYTHON")

        // Update the path
        this.path = path
        await tick()

        try {


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
                    await shell({ fn: "uv", cmd: "init", cwd: path })
                    return true
                }
            )

            if (!cont) return

            await step("Upsert 'link-mode: copy' to pyproject.toml",
                async () => {
                    const parsed = parse(await readTextFile(path + "/pyproject.toml")) as any;
                    if (parsed.tool === undefined) parsed.tool = {}
                    if (parsed.tool.uv === undefined) parsed.tool.uv = {}
                    if (parsed.tool.uv["link-mode"] === undefined) parsed.tool.uv["link-mode"] = "copy"

                    await writeTextFile(path + "/pyproject.toml", stringify(parsed))
                }
            )

            await step("Create data directory if not exist",
                async () => {
                    if (!await exists(path + "/data"))
                        await mkdir(path + "/data")
                }
            )

            await step("Install required dependencies",
                async () => {
                    await shell({ fn: "uv", cmd: "add git+https://github.com/qosUoG/Beinn#subdirectory=packages/cnoc --branch revert_threading", cwd: path })

                    await shell({ fn: "uv", cmd: "sync", cwd: path })
                    await shell({ fn: "uv", cmd: "add fastapi", cwd: path })
                    await shell({ fn: "uv", cmd: "add fastapi[standard]", cwd: path })
                    await shell({ fn: "uv", cmd: "add aiosqlite", cwd: path })

                    // In case cnoc is already installed and stale
                    await shell({ fn: "uv", cmd: "lock --upgrade-package cnoc", cwd: path })
                }
            )

            await step("Start python as a child process",
                async () => {
                    const handler = Command.create(
                        "uv", "run cnoc".split(" "), {
                        encoding: "utf8",
                        cwd: path
                    })
                    handler.stdout.on("data", async (message) => { await pushLog("meall", message) })
                    handler.stderr.on("data", async (message) => { await pushLog("meall", message) })

                    this.uvproc = await handler.spawn()
                }
            )

            // Get dependencies
            await this.get_dependencies()

            await sleep(2000) // Wait for uv to start


            // Connect to the websocket

            this.workspace_ws = new WebSocket(ws_url)

            this.workspace_ws.onmessage = workspaceOnMessage

            this.workspace_ws.onopen = () => {
                this.connected = true
            }

            this.workspace_ws.onclose = () => {
                this.connected = false
            }

            await completed()

        } catch (e) {
            await unhandled(e)
        }
    }


    /* 
    Update list of dependencies
    */
    async get_dependencies() {
        if (this.path === null) {
            console.error("workspace path should not be null")
            return
        }

        const uv_dependencies: Dependency[] = []

        // First prepare the dependencies already installed in the workspace
        const parsed = parse(await readTextFile(this.path + "/pyproject.toml"))

        const sources = (parsed.tool as { uv: { sources: Record<string, object> } }).uv?.sources


        for (const dependency of (parsed.project as { dependencies: string[] }).dependencies) {

            const parsed_dependency = dependency.match(/[A-Za-z_]+[A-Za-z\-_0-9]+/g)![0]


            if (!(parsed_dependency in sources))
                uv_dependencies.push({
                    source: { type: "pip", package: parsed_dependency },
                    name: parsed_dependency,
                    fullname: dependency,

                })

            else if ("git" in sources[parsed_dependency])
                uv_dependencies.push({
                    name: parsed_dependency,
                    fullname: dependency,
                    source: { type: "git", ...(sources[parsed_dependency] as Omit<GitSource, "type">) },

                })
            else if ("path" in sources[parsed_dependency])
                uv_dependencies.push({
                    name: parsed_dependency,
                    fullname: dependency,
                    source: { type: "path", ...(sources[parsed_dependency] as Omit<PathSource, "type">) },
                })
        }



        this.dependencies = uv_dependencies
    }

    async uninstallDependency(name: string) {


        const { step, completed, unhandled, failed } = await beginProcedure("DELETE DEPENDENCY")

        try {


            await step("Remove " + name + " from the workspace",
                async () => {
                    if (this.path === null) {
                        await failed("workspace path should not be null")
                        return
                    }
                    await shell({ fn: "uv", cmd: "remove " + name, cwd: this.path })
                }
            )

            // Refresh the dependencies
            await this.get_dependencies()

            await completed()
        } catch (e) {
            await unhandled(e)
        }

    }

    async installDependency(source: DependencySource) {
        const { step, completed, unhandled, failed } = await beginProcedure("INSTALL DEPENDENCY")

        try {
            await step("Installing " + source.type + " dependency",
                async () => {

                    if (this.path === null) {
                        await failed("workspace path should not be null")
                        return
                    }

                    switch (source.type) {
                        case "git": {
                            await shell({ fn: "uv", cmd: `add git+${source.git}${source.subdirectory !== "" ? "#subdirectory=" + source.subdirectory : ""}${source.branch !== "" ? " --branch " + source.branch : ""}`, cwd: this.path })
                            break
                        }

                        case "path": {
                            await shell({ fn: "uv", cmd: `add ${source.path}${source.editable ? "--editable" : ""}`, cwd: this.path })
                            break
                        }
                        case "pip": {
                            await shell({ fn: "uv", cmd: `add ${source.package}`, cwd: this.path })
                            break
                        }
                    }
                }
            )

            // Refresh the dependencies
            await this.get_dependencies()

            await completed()
        } catch (e) {
            await unhandled(e)
        }
    }


}

function workspaceOnMessage() {

}

export const controller = $state(new AppController())