
import { app_state, postCli } from "./app_state.ts"
import { parse, stringify } from "smol-toml"
import { applicationError, isErr, retryOnError, type DependencyT, type Save } from "@qoslab/shared";
import { mergeReadableStreams } from "jsr:@std/streams";
import { procIsRunning } from "./utils.ts";


export async function shell(command: string, path: string) {

    const process = new Deno.Command(command.split(" ")[0], {
        args: command.split(" ").toSpliced(0, 1),
        stdout: "piped",
        stderr: "piped",
        cwd: path
    }).spawn()

    const joined = mergeReadableStreams(
        process.stdout,
        process.stderr,
    );

    for await (const line of joined) {

        postCli("backend", new TextDecoder().decode(line))
    }
}

export async function initiateWorkspace(path: string) {
    try {


        // init barebone project
        await shell("uv init", path)

        // check if uv init successfully
        const res = await Deno.readTextFile(path + "/pyproject.toml")


        // add link-mode = true to pyproject.toml
        const parsed = parse(res)
        parsed.tool = { uv: { "link-mode": "copy" } }
        await Deno.writeTextFile(path + "/pyproject.toml", stringify(parsed))

    } catch (e) {
        if (e instanceof Deno.errors.NotFound)
            throw applicationError("Failed to run uv init, pyproject.toml not found")

        if (isErr(e)) throw e

        throw applicationError(`Error in backend initiateWorkspace: ${e}`)
    }


}

export async function copyApp(path: string) {
    let res: string

    try {

        // check if .gitignore exists
        res = await Deno.readTextFile(path + "/.gitignore")

    } catch (e) {
        if (!(e instanceof Deno.errors.NotFound))
            throw applicationError(`Error in backend copyApp: ${e}`)

        res = ""
    }

    try {
        // make sure .app in gitignore
        const gitignores = res.split("\n")
        if (!gitignores.includes("app")) await Deno.writeTextFile(path + "/.gitignore", [...gitignores, "app"].join("\n"))


        // install all dependency
        await shell("uv add fastapi fastapi[standard] aiosqlite", path)
        await shell("uv add git+https://github.com/qosUoG/Beinn#subdirectory=packages/beinnpy --branch main", path)

        // In case beinnpy is already installed and stale
        await shell("uv lock --upgrade-package beinnpy", path)
        await shell("uvx copier copy git+https://github.com/qosUoG/Beinn.git ./app", path)
    } catch (e) {
        if (isErr(e)) throw e
        throw applicationError(`Error in backend copyApp: ${e}`)
    }

}

export async function readAllUvDependencies(path: string) {
    try {
        // Get the list of dependencies from pyproject.toml
        const parsed = parse(await Deno.readTextFile(path + "/pyproject.toml"))

        const sources = (parsed.tool as { uv: { sources: Record<string, object> } }).uv?.sources

        const res: DependencyT[] = []

        for (const dependency of (parsed.project as { dependencies: string[] }).dependencies) {

            const parsed_dependency = dependency.match(/[A-Za-z_]+[A-Za-z\-_0-9]+/g)![0]


            if (!(parsed_dependency in sources))
                res.push({
                    source: { type: "pip", package: parsed_dependency },
                    name: parsed_dependency,
                    fullname: dependency,
                    installed: true,

                })
            else if ("git" in sources[parsed_dependency])
                res.push({
                    name: parsed_dependency,
                    fullname: dependency,
                    source: { type: "git", ...(sources[parsed_dependency] as { git: string, subdirectory: string, branch: string }) },
                    installed: true,

                })
            else if ("path" in sources[parsed_dependency])
                res.push({
                    name: parsed_dependency,
                    fullname: dependency,
                    source: { type: "path", ...(sources[parsed_dependency] as { path: string, editable: boolean }) },
                    installed: true,

                })



        }
        // return the list of dependencies
        return res

    } catch (e) {
        if (e instanceof Deno.errors.NotFound) throw applicationError("Failed read uv dependencies, pyproject.toml not found")
        if (isErr(e)) throw e
        throw applicationError(`Error in backend readAllUvDependencies: ${e}`)
    }
}

async function forever(joined: ReadableStream) {
    for await (const line of joined) {
        postCli("qoslabapp", new TextDecoder().decode(line))
    }

}



export async function runProject(path: string) {

    try {

        try {
            await Deno.mkdir(path + "/data")
        } catch (e) {
            if (!(e instanceof Deno.errors.AlreadyExists))
                throw applicationError("Failed to create ./data directory")
        }


        if (await procIsRunning(app_state.pyproc))
            throw applicationError("Failed to run project. pyproc still running")

        app_state.pyproc = new Deno.Command("uv", {
            args: "run uvicorn app.main:app --host localhost --port 8000".split(" "),
            stdout: "piped",
            stderr: "piped",
            cwd: path
        }).spawn()

        const joined = mergeReadableStreams(
            app_state.pyproc.stdout,
            app_state.pyproc.stderr,
        );

        forever(joined)


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
        return JSON.parse(await Deno.readTextFile(path + "/.qoslabapp_state"))
    } catch (e) {
        if (e instanceof Deno.errors.NotFound) return undefined
        if (isErr(e)) throw e
        throw applicationError(`Error in backend loadWorkspace: ${e}`)
    }
}

export async function saveWorkspace(path: string, save: Save) {
    try {
        await Deno.writeTextFile(path + "/.qoslabapp_state", JSON.stringify(save))
    } catch (e) {
        if (isErr(e)) throw e
        throw applicationError(`Error in backend saveWorkspace: ${e}`)
    }
}

