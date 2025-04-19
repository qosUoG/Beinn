import type { DependencyT_Installed } from "$states/dependency.svelte"
import { gstore } from "$states/global.svelte"
import { readTextFile } from "@tauri-apps/plugin-fs"
import { parse } from "smol-toml"
import { applicationError, isErr, type Result } from "$states/err"
import { fetch } from "@tauri-apps/plugin-http"

export function getRandomId(targetKeySet: string[]) {
    let res = window.crypto.randomUUID()
    while (targetKeySet.includes(res))
        res = window.crypto.randomUUID()

    return res
}

export async function readAllUvDependencies() {
    const uv_dependencies: DependencyT_Installed[] = []

    // First prepare the dependencies already installed in the workspace
    const parsed = parse(await readTextFile(gstore.workspace.path + "/pyproject.toml"))

    const sources = (parsed.tool as { uv: { sources: Record<string, object> } }).uv?.sources


    for (const dependency of (parsed.project as { dependencies: string[] }).dependencies) {

        const parsed_dependency = dependency.match(/[A-Za-z_]+[A-Za-z\-_0-9]+/g)![0]


        if (!(parsed_dependency in sources))
            uv_dependencies.push({
                source: { type: "pip", package: parsed_dependency },
                name: parsed_dependency,
                fullname: dependency,
                installed: true,

            })
        else if ("git" in sources[parsed_dependency])
            uv_dependencies.push({
                name: parsed_dependency,
                fullname: dependency,
                source: { type: "git", ...(sources[parsed_dependency] as { git: string, subdirectory: string, branch: string }) },
                installed: true,

            })
        else if ("path" in sources[parsed_dependency])
            uv_dependencies.push({
                name: parsed_dependency,
                fullname: dependency,
                source: { type: "path", ...(sources[parsed_dependency] as { path: string, editable: boolean }) },
                installed: true,
            })
    }
    return uv_dependencies
}




export const postRequestJsonInOut = async (url: string, payload: Record<any, any>, headers: HeadersInit = {
    "Content-type": "application/json"
}) => {
    let res
    try {

        res = await fetch(url, {
            method: "POST",
            body: JSON.stringify(payload),
            headers
        })
        if (!res.ok) throw applicationError(`Failed to POST at ${url} with payload ${JSON.stringify(payload)}`)


    } catch (e) {

        if (isErr(e)) throw e
        throw applicationError(`fetch threw error at ${url} with payload ${JSON.stringify(payload)}, error: ${JSON.stringify(e)}`)
    }

    let txt
    try {
        txt = await res.text()

        const obj = JSON.parse(txt) as Result
        if (!obj.success) throw obj.err
        return obj.value
    }
    catch (e) {

        if (isErr(e)) throw e
        throw applicationError(`json parsing threw error at ${url} with payload ${JSON.stringify(payload)}, returning ${txt}, error: ${JSON.stringify(e)}`)
    }

}




