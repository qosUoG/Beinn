import { $, file, randomUUIDv7, spawn, write } from "bun"
import { app_state } from "./app_state"
import { parse, stringify } from "smol-toml"
import type { Dependency } from "qoslab-shared";


export async function createProject(path: string) {
    $.cwd(path);
    // TODO Check if uv exists

    // init barebone project
    await $`uv init`

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
    $.cwd(path);
    // check if .gitignore exists
    const gitignore = file(path + "/.gitignore")

    if (! await gitignore.exists())
        await write(path + "/.gitignore", ".app")
    else {
        // make sure .app in gitignore
        const gitignores = (await file(path + "/.gitignore").text()).split("\n")
        if (!gitignores.includes(".app")) await write(path + "/.gitignore", [...gitignores, ".app"].join("\n"))
    }

    // install all dependency
    await $`uv add fastapi fastapi[standard] git+https://github.com/qosUoG/QosLab#subdirectory=packages/qoslablib`
    await $`uvx copier copy git+https://github.com/qosUoG/QosLab.git ./.app`
}

export async function addDependency(identifier: string, path: string) {
    $.cwd(path)
    // Could be from pip, git path or local path
    await $`uv add ${identifier}`
}

export async function removeDependency(name: string, path: string) {
    // Remove with the identifier
    $.cwd(path)
    await $`uv remove ${name}`
}

export async function readDependencies(path: string) {
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
                source: { type: "pip" },
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

export async function readModules(path: string,) {
    await syncUvScyn(path)
    $.cwd(path)

    // Get list of modules in the venv
    const modules = JSON.parse(await $`uv pip list --format json`.text()) as { name: string, version: string }[]

    return { modules }

}

export async function syncUvScyn(path: string) {
    $.cwd(path)
    await $`uv sync`
}

export function runProject(path: string) {

    if (app_state.pyproc === undefined || app_state.pyproc.killed) {

        app_state.pyproc = spawn(
            ["uv", "run", "uvicorn", "app.main:app", "--host", "localhost", "--port", "8000"],
            { stdout: "inherit", cwd: path }
        )

    }


}