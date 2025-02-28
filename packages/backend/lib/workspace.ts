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

    // install all dependency
    await $`uv add fastapi`
    await $`uv add fastapi[standard]`
    await $`uv add git+https://github.com/qosUoG/QosLab#subdirectory=packages/qoslablib`
    await $`uvx copier copy git+https://github.com/qosUoG/QosLab.git ./app`
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

export function runProject(path: string) {

    if (app_state.pyproc === undefined || app_state.pyproc.killed) {
        console.log("launched")
        app_state.pyproc = spawn(
            ["uv", "run", "fastapi", "run", "app/main.py"],
            { stdout: "inherit", cwd: path }
        )
        console.log(app_state.pyproc.pid)
    }


}