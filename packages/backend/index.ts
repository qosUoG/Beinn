import { randomUUIDv7, serve, type ServerWebSocket, type Subprocess } from "bun"
import { type ToBackendMessage, type ToFrontendMessage } from "shared-types"
import { getDirectoryInfo } from "./handlers/set_directory";

const ws_map: Map<string, ServerWebSocket<undefined>> = new Map()

const py_map: Map<string, Subprocess> = new Map()

serve<undefined>({
    port: 4000,
    hostname: "localhost",
    fetch(req, server) {

        const url = new URL(req.url)

        if (url.pathname === "/backend") {

            const success = server.upgrade(req, {});
            return success
                ? undefined
                : new Response("WebSocket upgrade errors", { status: 400 });
        }




    },
    websocket: {
        open(ws) {
            ws_map.entries().forEach(([k, v]) => {
                v.close()
                ws_map.delete(k)
                console.log(`ws connection ${k} closed`)
            })

            const id = randomUUIDv7()
            ws_map.set(id, ws)

            console.log(`backend: Connection ${id} opened`)

        },
        async message(ws, message: string) {

            function send<T extends ToFrontendMessage>(message: T) {
                ws.send(JSON.stringify(message))
            }




            const msg = JSON.parse(message) as ToBackendMessage
            switch (msg.command) {
                case "Set-Directory":
                    send({
                        command: "Project-Directory-Info",
                        payload: await getDirectoryInfo(msg.payload.path)
                    })
                    break;
                case "Start-Experiment":

                    py_map.entries().forEach(([k, v]) => {
                        v.kill()
                        py_map.delete(k)
                        console.log(`py proc ${k} killed`)
                    })
                    const pyproc = Bun.spawn(["uv", "run", msg.payload.script_name], {
                        cwd: msg.payload.cwd,
                        stdout: "inherit"
                    })

                    const id = randomUUIDv7()
                    py_map.set(id, pyproc)

                    console.log(`backend: py proc ${id} started`)

                    break

            }
        },
    }
})

