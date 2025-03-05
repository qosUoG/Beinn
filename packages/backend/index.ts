import { serve } from "bun"
import { getDirectoryInfo, pathExist } from "./lib/fs";

import { mkdir, readdir } from "node:fs/promises";

import { addDependency, checkDependency, copyApp, createProject, readDependencies, readModules, removeDependency, runProject } from "./lib/workspace";
import { app_state } from "./lib/app_state";

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


const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS, POST',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

serve({
    port: 4000,
    hostname: "localhost",
    routes: {
        "/workspace/set_directory": {
            POST: async req => {

                const { path } = await req.json() as { path: string }

                const path_exist = await pathExist(path)

                if (!path_exist) {
                    await mkdir(path)
                    await createProject(path)

                }

                if (!await pathExist(path + "/app"))
                    await copyApp(path)


                runProject(path)
                return Response.json(await getDirectoryInfo(path), { headers })
            }
        },
        "/workspace/check_dependency": {
            POST: async req => {

                const { path, source } = await req.json() as { source: string, path: string }

                return Response.json({ success: await checkDependency(path, source) }, { headers })
            }
        },
        "/workspace/add_dependency": {
            POST: async req => {

                const { path, source } = await req.json() as { source: string, path: string }
                await addDependency(path, source)
                return Response.json({}, { headers })
            }
        },
        "/workspace/remove_dependency": {
            POST: async req => {

                const { path, name } = await req.json() as { name: string, path: string }
                await removeDependency(path, name)
                return Response.json({}, { headers })
            }
        },
        "/workspace/read_dependency": {
            POST: async req => {
                const { path } = await req.json() as { path: string }
                return Response.json(await readDependencies(path), { headers })
            }
        },
        "/workspace/read_modules": {
            POST: async req => {
                const { path } = await req.json() as { path: string }
                return Response.json(await readModules(path), { headers })
            }
        }
    },
    async fetch(req) {

        // Handle CORS preflight requests
        if (req.method === 'OPTIONS') {
            const res = new Response('', { headers });
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

