import type { DependencyT_Installed } from "$states/dependency.svelte"

import { readTextFile } from "@tauri-apps/plugin-fs"
import { parse } from "smol-toml"
import { fetch } from "@tauri-apps/plugin-http"
import { Command } from "@tauri-apps/plugin-shell";
import { pushLog } from "$components/modules/LogPanelController.svelte"
import { workspace } from "$states/workspace.svelte"

export function zeropad(num: number) {
    if (num < 10) return `0${num}`;
    return `${num}`;
}

export function getRandomId(targetKeySet: string[]) {
    let res = window.crypto.randomUUID()
    while (targetKeySet.includes(res))
        res = window.crypto.randomUUID()

    return res
}

export async function readAllUvDependencies() {
    const uv_dependencies: DependencyT_Installed[] = []

    // First prepare the dependencies already installed in the workspace
    const text = await readTextFile(workspace.path + "/pyproject.toml")
    const parsed = parse(await readTextFile(workspace.path + "/pyproject.toml"))

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




export const postRequestJsonInOut_throwable = async (url: string, payload: Record<any, any>, headers: HeadersInit = {
    "Content-type": "application/json"
}) => {

    const res = await fetch(url, {
        method: "POST",
        body: JSON.stringify(payload),
        headers
    })

    const txt = await res.text()


    let obj
    try {
        obj = JSON.parse(txt)
    }
    catch (e) {
        throw Error(`failed to parse ${txt} to json`)
    }

    if (!obj.success) {
        if (obj.err)
            throw obj.err

        throw Error(`failed to get obj.err from ${JSON.stringify(obj)}`)
    }

    return obj.value
}

export const getRequestJsonOut_throwable = async (url: string) => {

    const res = await fetch(url)
    const txt = await res.text()

    let obj
    try {
        obj = JSON.parse(txt)
    }
    catch (e) {
        throw Error(`failed to parse ${txt} to json`)
    }

    if (!obj.success) {
        if (obj.err)
            throw obj.err

        throw Error(`failed to get obj.err from ${JSON.stringify(obj)}`)
    }

    return obj.value
}

export async function shell({ fn, cmd, cwd }: { fn: string, cmd: string, cwd: string }) {

    const handler = Command.create(
        fn, cmd.split(" "), {
        encoding: "utf8",
        cwd
    })
    const p = new Promise((resolve) => {
        handler.on("close", resolve)
        handler.on("error", resolve)
    })

    await pushLog('beinn', `SHELL\n        cwd:${cwd}\n        ${fn} ${cmd}\n`)



    handler.stdout.on("data", async (message) => { await pushLog("beinn", "        " + message) })
    handler.stderr.on("data", async (message) => { await pushLog("beinn", "        " + message) })

    await handler.spawn()
    await p
}


export async function timeoutLoop(timeout_ms: number, fn: () => Promise<boolean>) {
    const timenow = Date.now();
    while ((Date.now() - timenow <= timeout_ms) && await fn()) { }

}

export async function retryOnError(timeout_ms: number, fn: () => Promise<void>) {
    await timeoutLoop(
        timeout_ms,
        async () => {
            try {
                // Fetch experiment and equipment
                await fn();
                return false
            } catch (error) {
                return true
            }
        }
    )
}

export function capitalise(input: string) { return input[0].toUpperCase() + String(input).slice(1); }

export const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

export type StepT<T = void> = (step_name: string, fn: () => (Promise<T> | T)) => Promise<T>

export async function beginProcedure(proc_name: string) {
    await pushLog("beinn", `PROCEDURE ${proc_name} --- BEGIN` + "\n")

    async function step<T = void>(step_name: string, fn: () => (Promise<T> | T)) {
        try {
            await pushLog("beinn", `${proc_name} --- STEP: ${step_name}\n`)
            const res = await fn()
            await pushLog("beinn", `${proc_name} --- STEP: ${step_name} --- SUCCESS\n`)
            return res
        } catch (e) {
            if (e && typeof (e) === "object" && "stack" in e)
                await pushLog("beinn", `${proc_name} --- STEP: ${step_name} --- FAILED\n    error:\n` + ((e).stack) + "\n")
            else if (e && typeof (e) === "object" && "toString" in e)
                await pushLog("beinn", `${proc_name} --- STEP: ${step_name} --- FAILED\n    error:\n    ` + e.toString() + "\n")
            else
                await pushLog("beinn", `${proc_name} --- STEP: ${step_name} --- FAILED\n    error:\n    ` + e + "\n")

            throw `ERROR HANDLED:${step_name}`
        }
    }


    async function completed() {
        await pushLog("beinn", `PROCEDURE ${proc_name} --- COMPLETED` + "\n")
    }
    async function cancelled(reason: string) {

        await pushLog("beinn", `PROCEDURE ${proc_name} --- CANCELLED\n    reason:\n    ${reason}` + "\n")
    }
    async function failed(reason: string) {
        await pushLog("beinn", `PROCEDURE ${proc_name} --- FAILED\n    reason:\n    ${reason}` + "\n")
    }
    async function unhandled(e: unknown) {
        if (typeof e === "string" && e.startsWith("ERROR HANDLED"))
            await pushLog("beinn", `${proc_name} --- FAILED at STEP ${e.split(":")[1]}` + "\n")


        else if (e && typeof (e) === "object" && "stack" in e)
            await pushLog("beinn", `${proc_name} --- FAILED\n    error:\n` + ((e).stack) + "\n")
        else if (e && typeof (e) === "object" && "toString" in e)
            await pushLog("beinn", `${proc_name} --- FAILED\n    error:\n    ` + e.toString() + "\n")
        else
            await pushLog("beinn", `${proc_name} --- FAILED\n    error:\n    ` + e + "\n")
    }



    return { step, completed, cancelled, failed, unhandled }
}