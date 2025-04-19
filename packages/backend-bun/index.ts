import { $, file, serve, type RouterTypes } from "bun"
import { headers } from "./lib/_shared";
import { app_state, postCli } from "./lib/app_state";
import { copyApp, initiateWorkspace, loadWorkspace, readAllUvDependencies, runProject, saveWorkspace, shell } from "./lib/workspace";
import { pathExist } from "./lib/fs";
import { mkdir } from "node:fs/promises"
import { applicationError, isErr, type Err, type Result } from "beinn-js";
import open from 'open';

import { embeddedFiles } from "bun"

// function consoleIterator(...data: any[]) {

//     postCli("backend", typeof data[0] === "string" ? data[0] : JSON.stringify(data[0]))
// }

// console.log = consoleIterator

console.log({ embeddedFiles })

const index_html = embeddedFiles.find((f) => f.name.startsWith("index") && f.name.endsWith(".html"))

const frontend_jss = embeddedFiles.find((f) => f.name.startsWith("frontend") && f.name.endsWith(".jss"))
const frontend_css = embeddedFiles.find((f) => f.name === "static/assets/frontend.css")

const worker_jss = embeddedFiles.find((f) => f.name.startsWith("worker") && f.name.endsWith(".jss"))

serve({
    port: 4000,
    hostname: "localhost",
    websocket: {
        open(ws) {

            app_state.ws = ws

            // Post all accumulated logs to the frontend
            if (app_state.logs.length > 0) {
                const logs = JSON.parse(JSON.stringify(app_state.logs))
                app_state.logs = []

                ws.send(JSON.stringify({ logs }))


            }
        },
        message(ws, message) {
            // The websocket is only used to post logs to the frontend. As such there is no message handler
        },
        close(ws) {
            app_state.ws = undefined
        }

    },

    routes: {
        "/": new Response(index_html),
        "/assets/frontend.jss": new Response(frontend_jss, { headers: { "Content-Type": "application/javascript" } }),
        "/assets/frontend.css": new Response(frontend_css),
        "/assets/worker-DJyNAymy.js": new Response(worker_jss, { headers: { "Content-Type": "application/javascript" } }),
        // "/vite.svg": new Response(embeddedFiles.find((f) => f.name === "vite.svg")),

        "/workspace/load": {
            POST: async req => {
                try {



                    const { path } = await req.json() as { path: string }

                    const path_exist = await pathExist(path)

                    if (!path_exist) {
                        await mkdir(path)
                        await initiateWorkspace(path)
                    }

                    if (!await pathExist(path + "/app"))
                        await copyApp(path)

                    await runProject(path)
                    return Response.json({ success: true, value: await loadWorkspace(path) }, { headers })

                } catch (e) {

                    if (isErr(e)) return Response.json({ success: false, err: e }, { headers })


                    return Response.json({ success: false, err: applicationError(`Error in backend /workspace/load: ${JSON.stringify(e)}`) }, { headers })
                }


            }
        }
        ,
        "/workspace/save": {
            POST: async req => {
                try {
                    const { path, save } = await req.json() as { path: string, save: any }
                    await saveWorkspace(path, save)
                    return Response.json({ success: true }, { headers })
                } catch (e) {
                    if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

                    return Response.json({ success: false, err: applicationError(`Error in backend /workspace/save: ${JSON.stringify(e)}`) }, { headers })
                }
            }
        }
        ,
        "/workspace/dependency/check_init": {
            POST: async req => {
                try {
                    const { path, directory } = await req.json() as { directory: string, path: string }
                    return Response.json({ success: await file(path + "/" + directory + "/__init__.py").exists() }, { headers })
                } catch (e) {
                    if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

                    return Response.json({ success: false, err: applicationError(`Error in backend /workspace/dependency/check_init: ${JSON.stringify(e)}`) }, { headers })
                }
            }
        },
        "/workspace/dependency/add": {
            POST: async req => {
                try {
                    const { path, source } = await req.json() as { source: string, path: string }

                    // Could be from pip, git path or local path
                    shell(`uv add ${{ raw: source }}`, path)
                    return Response.json({ success: true }, { headers })

                } catch (e) {
                    if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

                    return Response.json({ success: false, err: applicationError(`Error in backend /workspace/dependency/add: ${JSON.stringify(e)}`) }, { headers })
                }
            }
        },
        "/workspace/dependency/remove": {
            POST: async req => {
                try {
                    const { path, name } = await req.json() as { name: string, path: string }

                    shell(`uv remove ${name}`, path)
                    return Response.json({ success: true }, { headers })
                } catch (e) {
                    if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

                    return Response.json({ success: false, err: applicationError(`Error in backend /workspace/dependency/remove: ${JSON.stringify(e)}`) }, { headers })
                }
            }
        },
        "/workspace/dependency/read_all": {
            POST: async req => {
                try {
                    const { path } = await req.json() as { path: string }
                    return Response.json({ success: true, value: await readAllUvDependencies(path) }, { headers })

                } catch (e) {
                    if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

                    return Response.json({ success: false, err: applicationError(`Error in backend /workspace/dependency/read_all: ${JSON.stringify(e)}`) }, { headers })
                }
            }
        },
        "/workspace/disconnect": {
            GET: async req => {
                try {
                    if (app_state.pyproc === undefined) {

                        return Response.json({ success: true }, { headers })
                    }

                    if (app_state.pyproc !== undefined) {
                        const res = await (await fetch("http://localhost:8000/workspace/forcestop")).json() as { success: boolean }
                        if (res.success) {
                            app_state.pyproc?.kill()
                            // wait for 100 ms
                            await new Promise(_ => setTimeout(_, 1000));

                            return Response.json({ success: true }, { headers })
                        }
                    }
                    throw applicationError("Cannot disconnect python procedure")

                } catch (e) {
                    if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

                    return Response.json({ success: false, err: applicationError(`Error in backend /workspace/disconnectl: ${JSON.stringify(e)}`) }, { headers })
                }
            }
        }
    },
    async fetch(req, server) {

        // Handle CORS preflight requests
        if (req.method === 'OPTIONS')
            return new Response('', { headers });

        const pathname = new URL(req.url).pathname



        // Upgrade to websocket
        if (pathname === "/cli" && server.upgrade(req)) {

            return undefined as unknown as Response; // do not return a Response
        }



        // if (pathname.startsWith("/assets")) {
        //     const file = Bun.file("./static" + pathname)

        //     return new Response(await file.bytes(), { headers: { "Content-Type": file.type } })
        // }


        return new Response('Not Found', { headers, status: 404 });
    },

});

open('http://localhost:4000');

process.on("SIGINT", async () => {

    if (app_state.pyproc !== undefined) {

        const res = await fetch("http://localhost:8000/workspace/forcestop")
        console.log(await res.json())
        app_state.pyproc?.kill()
        // wait for 100 ms
        await new Promise(_ => setTimeout(_, 1000));
    }

    process.exit();
});