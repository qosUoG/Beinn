import { $, file, randomUUIDv7, serve, write, type ServerWebSocket, type Subprocess } from "bun"
import { getDirectoryInfo, path_exist } from "./lib/set_directory";
import { Readable } from 'node:stream'
import { access, constants, mkdir, stat } from "node:fs/promises";
import { parse, stringify } from 'smol-toml'

// const ws_map: Map<string, ServerWebSocket<undefined>> = new Map()

// const py_map: Map<string, Subprocess> = new Map()

// process.on("SIGINT", () => {
//     // Gracefully stop pyproc
//     py_map.entries().forEach(([k, v]) => {
//         v.kill()
//         py_map.delete(k)
//         console.log(`py proc ${k} killed`)
//     })

//     // Gracefully stop websocket
//     ws_map.entries().forEach(([k, v]) => {
//         v.close()
//         ws_map.delete(k)
//         console.log(`ws connection ${k} closed`)
//     })

//     console.log("Backend Process killed")

//     process.exit()
// })

let state: {
    workspace: {
        path: string
    },
    dependencies: string[]
} = {
    workspace: {
        path: ""
    },
    dependencies: []
}

const CORS_HEADERS = {

    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS, POST',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',

};

serve({
    port: 4000,
    hostname: "localhost",
    routes: {
        "/workspace/set_directory": {
            POST: async req => {

                const payload = await req.json() as { path: string }

                // Check if the directory exist
                if (! await path_exist(payload.path)) {
                    await mkdir(payload.path)
                    // Check if uv exists
                    $.cwd(payload.path);
                    $`uv init`

                    // check if uv init successfully
                    const pyproject = file(payload.path + "/pyproject.toml")
                    if (! await pyproject.exists()) throw Error()

                    // add link-mode = true to pyproject.toml
                    let parsed = parse(await pyproject.text())
                    parsed.tools.uv['link-mode'] = true
                    await write(payload.path + "/pyproject.toml", stringify(parsed))

                    // install all dependency
                    $`uv add fastapi`
                    $`uv add fastapi[standard]`
                    $`uv add uv add git+https://github.com/qosUoG/QosLab#subdirectory=packages/qoslab-lib`
                    $`uvx copier copy git+https://github.com/qosUoG/QosLab.git ./app`
                }


                state.workspace.path = payload.path



                return Response.json(await getDirectoryInfo(payload.path), {
                    headers: {
                        ...CORS_HEADERS
                    }
                })
            }
        },
        "/workspace/add_dependency": {
            POST: async req => {

                const payload = await req.json() as { path: string }
                state.workspace.path = payload.path
                return Response.json(await getDirectoryInfo(payload.path), {
                    headers: {
                        ...CORS_HEADERS
                    }
                })
            }
        }
    },
    async fetch(req) {

        // Handle CORS preflight requests
        if (req.method === 'OPTIONS') {
            const res = new Response('', { headers: CORS_HEADERS });
            return res;
        }

        return new Response()
    }
    // fetch(req, server) {

    //     const url = new URL(req.url)

    //     switch (url.pathname) {

    //         case "workspace/set_directory":
    //             await getDirectoryInfo(msg.payload.path)
    //     }




    // },
    // websocket: {
    //     open(ws) {
    //         ws_map.entries().forEach(([k, v]) => {
    //             v.close()
    //             ws_map.delete(k)
    //             console.log(`ws connection ${k} closed`)
    //         })

    //         const id = randomUUIDv7()
    //         ws_map.set(id, ws)

    //         console.log(`backend: Connection ${id} opened`)

    //     },
    //     async message(ws, message: string) {

    //         function send<T extends ToFrontendMessage>(message: T) {
    //             ws.send(JSON.stringify(message))
    //         }




    //         const msg = JSON.parse(message) as ToBackendMessage
    //         switch (msg.command) {
    //             case "Set-Directory":
    //                 send({
    //                     command: "Project-Directory-Info",
    //                     payload: await getDirectoryInfo(msg.payload.path)
    //                 })
    //                 break;
    //             case "Start-Experiment":

    //                 py_map.entries().forEach(([k, v]) => {
    //                     v.kill()
    //                     py_map.delete(k)
    //                     console.log(`py proc ${k} killed`)
    //                 })

    //                 const pyproc = Bun.spawn(["uv", "run", msg.payload.script_name], {
    //                     cwd: msg.payload.cwd,
    //                 })

    //                 async function logPyProc() {
    //                     let out = ""
    //                     const stdout = Readable.fromWeb(pyproc.stdout)
    //                     while (true) {
    //                         console.log("here")

    //                         // out = await new Response(pyproc.stdout).text()
    //                         for await (const x of stdout) {

    //                             console.log(`STDOUT: ${x}`)
    //                         }

    //                     }
    //                 }

    //                 logPyProc()

    //                 const id = randomUUIDv7()
    //                 py_map.set(id, pyproc)

    //                 console.log(`backend: py proc ${id} started`)

    //                 break

    //         }
    //     },
    // }
})

