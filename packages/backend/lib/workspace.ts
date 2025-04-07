import { $, fetch, file, randomUUIDv7, spawn, spawnSync, write, type SpawnOptions } from "bun"
import { app_state, postCli } from "./app_state"
import { parse, stringify } from "smol-toml"
import { applicationError, isErr, retryOnError, type DependencyT, type Result } from "qoslab-shared";
import { pathExist } from "./fs";
import { mkdir } from "node:fs/promises";

export function shell(command: string, path: string) {
    postCli("backend", spawnSync(command.split(" "),
        { cwd: path }).stderr.toString())
}

export async function initiateWorkspace(path: string) {
    try {


        // init barebone project
        shell("uv init", path)

        // check if uv init successfully
        const pyproject = file(path + "/pyproject.toml")
        if (! await pyproject.exists()) throw applicationError("Failed to run uv init, pyproject.toml not found")

        // add link-mode = true to pyproject.toml
        const res = await pyproject.text()
        let parsed = parse(res) as any
        parsed.tool = { uv: { "link-mode": "copy" } }
        await write(path + "/pyproject.toml", stringify(parsed))

    } catch (e) {
        if (isErr(e)) throw e

        throw applicationError(`Error in backend initiateWorkspace: ${e}`)
    }


}

export async function copyApp(path: string) {

    try {
        // check if .gitignore exists
        const gitignore = file(path + "/.gitignore")

        if (! await gitignore.exists())
            await write(path + "/.gitignore", "app")
        else {
            // make sure .app in gitignore
            const gitignores = (await file(path + "/.gitignore").text()).split("\n")
            if (!gitignores.includes("app")) await write(path + "/.gitignore", [...gitignores, "app"].join("\n"))
        }

        // install all dependency
        shell("uv add fastapi fastapi[standard] aiosqlite", path)
        shell("uv add git+https://github.com/qosUoG/QosLab#subdirectory=packages/qoslablib --branch main", path)

        // In case qoslablib is already installed and stale
        shell("uv lock --upgrade-package qoslablib", path)
        shell("uvx copier copy git+https://github.com/qosUoG/QosLab.git ./app", path)
    } catch (e) {
        if (isErr(e)) throw e
        throw applicationError(`Error in backend copyApp: ${e}`)
    }

}

export async function readAllUvDependencies(path: string) {
    try {
        // Get the list of dependencies from pyproject.toml
        const pyproject = file(path + "/pyproject.toml")
        if (! await pyproject.exists()) throw applicationError("Failed read uv dependencies, pyproject.toml not found")

        const parsed = parse(await pyproject.text()) as any

        const sources = parsed.tool?.uv?.sources

        let res: DependencyT[] = []

        for (const dependency of parsed.project.dependencies as string[]) {

            const parsed_dependency = dependency.match(/[A-Za-z_]+[A-Za-z\-_0-9]+/g)![0]

            let type = "pip"
            if (!(parsed_dependency in sources)) {
                res.push({
                    source: { type: "pip", package: parsed_dependency },
                    name: parsed_dependency,
                    fullname: dependency,
                    installed: true,

                })
                continue
            }

            if ("git" in sources[parsed_dependency])
                type = "git"
            else if ("path" in sources[parsed_dependency])
                type = "path"

            res.push({
                name: parsed_dependency,
                fullname: dependency,
                source: { type, ...sources[parsed_dependency] },
                installed: true,

            })

        }
        // return the list of dependencies
        return { dependencies: res }

    } catch (e) {
        if (isErr(e)) throw e
        throw applicationError(`Error in backend readAllUvDependencies: ${e}`)
    }
}

export async function runProject(path: string) {

    try {

        if (!(await pathExist(path + "/data")))
            await mkdir(path + "/data")


        if (app_state.pyproc !== undefined && !app_state.pyproc.killed)
            throw applicationError("Failed to run project. pyproc still running")

        app_state.pyproc = spawn(
            "uv run uvicorn app.main:app --host localhost --port 8000".split(" "),
            { stdout: "pipe", cwd: path }
        )

        async function forever() {
            interface ReadableStream<R = any> {
                [Symbol.asyncIterator](): AsyncIterableIterator<R>;
            }

            for await (const line of app_state.pyproc!.stdout as unknown as ReadableStream) {
                const output = await new Response(line).text();
                postCli("qoslabapp", output)
            }


        }

        forever()


        // Wait until the app is online
        await retryOnError(5000, async () => {
            const res = await (await fetch("http://localhost:8000/workspace/status")).json();
            if (res.status !== "online")
                throw Error()
        });

        const res = await (await fetch("http://localhost:8000/workspace/status")).json();
        if (res.status !== "online")
            throw applicationError("Timeout in backend runProject. Project is not online")
    } catch (e) {
        if (isErr(e)) throw e
        throw applicationError(`Error in backend runProject: ${e}`)
    }


}

export async function loadWorkspace(path: string) {

    try {
        const save_file = file(path + "/.qoslabapp_state")
        if (!(await save_file.exists())) return { save: undefined }

        return { save: JSON.parse(await save_file.text()) }

    } catch (e) {
        if (isErr(e)) throw e
        throw applicationError(`Error in backend loadWorkspace: ${e}`)
    }
}

export async function saveWorkspace(path: string, payload: any) {
    try {
        const save_file = file(path + "/.qoslabapp_state")
        await save_file.write(JSON.stringify(payload))
    } catch (e) {
        if (isErr(e)) throw e
        throw applicationError(`Error in backend saveWorkspace: ${e}`)
    }
}

