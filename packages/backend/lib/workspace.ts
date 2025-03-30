import { $, fetch, file, randomUUIDv7, spawn, spawnSync, write, type SpawnOptions } from "bun"
import { app_state, postCli } from "./app_state"
import { parse, stringify } from "smol-toml"
import { retryOnError, type Dependency } from "qoslab-shared";
import { pathExist } from "./fs";
import { mkdir } from "node:fs/promises";

function shell(command: string, path: string) {
    const text = spawnSync(command.split(" "),
        { cwd: path }).stderr.toString()
    console.log(JSON.stringify({ text }))
    postCli("backend", text)
}

export async function initiateWorkspace(path: string) {
    // TODO Check if uv exists

    // init barebone project
    shell("uv init", path)


    // check if uv init successfully
    const pyproject = file(path + "/pyproject.toml")
    if (! await pyproject.exists()) throw Error()

    // add link-mode = true to pyproject.toml
    const res = await pyproject.text()
    let parsed = parse(res) as any
    parsed.tool = { uv: { "link-mode": "copy" } }
    await write(path + "/pyproject.toml", stringify(parsed))


}

export async function copyApp(path: string) {

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

}

export async function readAllUvDependencies(path: string) {
    // Get the list of dependencies from pyproject.toml
    const pyproject = file(path + "/pyproject.toml")
    if (! await pyproject.exists()) throw Error()

    const parsed = parse(await pyproject.text()) as any

    const sources = parsed.tool?.uv?.sources

    let res: Dependency[] = []

    for (const dependency of parsed.project.dependencies as string[]) {

        const parsed_dependency = dependency.match(/[A-Za-z_]+[A-Za-z\-_0-9]+/g)![0]

        let type = "pip"
        if (!(parsed_dependency in sources)) {
            res.push({
                id: randomUUIDv7(),
                source: { type: "pip", package: parsed_dependency },
                name: parsed_dependency,
                fullname: dependency,
                confirmed: true
            })
            continue
        }


        if ("git" in sources[parsed_dependency])
            type = "git"
        else if ("path" in sources[parsed_dependency])
            type = "path"


        res.push({
            id: "",
            name: parsed_dependency,
            fullname: dependency,
            source: { type, ...sources[parsed_dependency] },
            confirmed: true
        })


    }
    // return the list of dependencies
    return { dependencies: res }
}

export async function runProject(path: string) {
    if (!(await pathExist(path + "/data")))
        await mkdir(path + "/data")


    if (app_state.pyproc !== undefined && !app_state.pyproc.killed)
        return

    app_state.pyproc = spawn(
        "uv run uvicorn app.main:app --host localhost --port 8000".split(" "),
        { stdout: "pipe", cwd: path }
    )

    async function forever() {


        interface ReadableStream<R = any> {
            [Symbol.asyncIterator](): AsyncIterableIterator<R>;
        }

        for await (const line of app_state.pyproc.stdout as unknown as ReadableStream) {
            const output = await new Response(line).text();
            postCli("qoslabapp", output)
        }

        // const output = await new Response(app_state.pyproc.stdout).text();
        // console.log(output)

        // for await (const out of app_state.pyproc!.stdout as unknown as ReadableStream) {
        //     console.log("printing")
        //     console.log(new Response(out).text())
        // }
    }

    forever()








    // Wait until the app is online
    await retryOnError(5000, async () => {
        const res = await (await fetch("http://localhost:8000/workspace/status")).json();
        if (res.status !== "online")
            throw Error()
    });


}

