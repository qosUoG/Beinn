
import { headers, procIsRunning } from "./lib/utils.ts";
import { app_state, postCli } from "./lib/app_state.ts";
import { copyApp, initiateWorkspace, loadWorkspace, readAllUvDependencies, runProject, saveWorkspace, shell } from "./lib/workspace.ts";
import { applicationError, isErr, type Save } from "@qoslab/shared";
import open from 'open';
import { contentType } from "jsr:@std/media-types";
import process from "node:process";
import { exists } from "jsr:@std/fs/exists";

// deno-lint-ignore no-explicit-any
function consoleIterator(...data: any[]) {
    postCli("backend", typeof data[0] === "string" ? data[0] : JSON.stringify(data[0]))
}

console.log = consoleIterator

const static_routes = {
    "/": async (_: Request) =>
        new Response((await Deno.open(import.meta.dirname + "/dist/index.html", { read: true })).readable, {
            headers: {
                "content-type": contentType(".html")
            }
        })
    ,
    "/workspace/load": async (req: Request) => {
        try {
            const { path } = await req.json() as { path: string }


            try {
                await Deno.mkdir(path)
                await initiateWorkspace(path)
            } catch (e) {
                if (isErr(e)) throw e

                if (!(e instanceof Deno.errors.AlreadyExists))
                    throw applicationError(`Failed to create ${path} directory`)
            }



            try {
                await Deno.lstat(path + "/app");
            } catch (e) {
                if (!(e instanceof Deno.errors.NotFound))
                    throw applicationError(`Error trying to check if ./app exists, error: ${e}`)

                await copyApp(path)
            }

            await runProject(path)
            return Response.json({ success: true, value: await loadWorkspace(path) }, { headers })

        } catch (e) {

            if (isErr(e)) return Response.json({ success: false, err: e }, { headers })


            return Response.json({ success: false, err: applicationError(`Error in backend /workspace/load: ${JSON.stringify(e)}`) }, { headers })
        }


    },
    "/workspace/save": async (req: Request) => {
        try {
            const { path, save } = await req.json() as { path: string, save: Save }
            await saveWorkspace(path, save)
            return Response.json({ success: true }, { headers })
        } catch (e) {
            if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

            return Response.json({ success: false, err: applicationError(`Error in backend /workspace/save: ${JSON.stringify(e)}`) }, { headers })
        }
    },
    "/workspace/dependency/check_init": async (req: Request) => {
        try {
            const { path, directory } = await req.json() as { directory: string, path: string }
            return Response.json({ success: await exists(path + "/" + directory + "/__init__.py") }, { headers })
        } catch (e) {
            if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

            return Response.json({ success: false, err: applicationError(`Error in backend /workspace/dependency/check_init: ${JSON.stringify(e)}`) }, { headers })
        }
    },
    "/workspace/dependency/add": async (req: Request) => {
        try {
            const { path, source } = await req.json() as { source: string, path: string }

            // Could be from pip, git path or local path
            shell(`uv add ${{ raw: source }}`, path)
            return Response.json({ success: true }, { headers })

        } catch (e) {
            if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

            return Response.json({ success: false, err: applicationError(`Error in backend /workspace/dependency/add: ${JSON.stringify(e)}`) }, { headers })
        }
    },
    "/workspace/dependency/remove": async (req: Request) => {
        try {
            const { path, name } = await req.json() as { name: string, path: string }

            shell(`uv remove ${name}`, path)
            return Response.json({ success: true }, { headers })
        } catch (e) {
            if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

            return Response.json({ success: false, err: applicationError(`Error in backend /workspace/dependency/remove: ${JSON.stringify(e)}`) }, { headers })
        }
    },
    "/workspace/dependency/read_all": async (req: Request) => {
        try {
            const { path } = await req.json() as { path: string }
            return Response.json({ success: true, value: await readAllUvDependencies(path) }, { headers })

        } catch (e) {
            if (isErr(e)) return Response.json({ success: false, err: e }, { headers })

            return Response.json({ success: false, err: applicationError(`Error in backend /workspace/dependency/read_all: ${JSON.stringify(e)}`) }, { headers })
        }
    },
    "/workspace/disconnect": async (_: Request) => {
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

Deno.serve({ hostname: "localhost", port: 4000 },
    async (req) => {
        const url = new URL(req.url);

        // Check if websocket

        if (req.headers.get("upgrade") === "websocket" && url.pathname === "/cli") {
            const { socket: ws, response } = Deno.upgradeWebSocket(req);
            ws.addEventListener("open", () => {
                app_state.ws = ws

                // Post all accumulated logs to the frontend
                if (app_state.logs.length > 0) {
                    const logs = JSON.parse(JSON.stringify(app_state.logs))
                    app_state.logs = []

                    ws.send(JSON.stringify({ logs }))


                }
            });

            ws.addEventListener("close", (_) => {
                app_state.ws = undefined
            });

            return response
        }

        // Static routes
        if (Object.keys(static_routes).includes(url.pathname)) {
            const handler = static_routes[url.pathname as keyof typeof static_routes]
            return await handler(req)
        }


        // For wild cards, try to serve the file
        try {
            return new Response((await Deno.open(import.meta.dirname + "/dist" + url.pathname, { read: true })).readable, {
                headers: {
                    "content-type": contentType("." + url.pathname.split(".").at(-1)) ?? "application/octet-stream"
                }
            })
        } catch (e) {
            if (e instanceof Deno.errors.NotFound) {
                return new Response(null, { status: 404 });
            }
            return new Response(null, { status: 500 });
        }

    })


open('http://localhost:4000');

process.on("SIGINT", async () => {

    if (await procIsRunning(app_state.pyproc)) {

        const res = await fetch("http://localhost:8000/workspace/forcestop")
        console.log(await res.json())
        app_state.pyproc?.kill()
        // wait for 100 ms
        await new Promise(_ => setTimeout(_, 1000));
    }

    process.exit();
});