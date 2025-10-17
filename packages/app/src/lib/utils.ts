
import { log_controller, type ShellEntry } from "$controllers/log.svelte"
import { Command } from "@tauri-apps/plugin-shell"

export const cnoc_url = "ws://localhost:8001/"

export type Prettify<T> = {
    [K in keyof T]: T[K];
} & {};

export function deepCopy<T>(obj: T): T {
    return JSON.parse(JSON.stringify(obj))
}

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

export const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));


export async function shell({ fn, cmd, description, cwd }:
    { fn: string, cmd: string | string[], description: string, cwd: string }) {
    const entry = log_controller.appendShell({
        cwd,
        command: typeof cmd === "string" ? cmd : cmd.join(" "),
        description,
        std: [],
        err: "",
        code: null
    })

    let stdout = ""

    const handler = Command.create(
        fn, typeof cmd === "string" ? cmd.split(" ") : cmd, {
        encoding: "utf8",
        cwd
    })

    handler.stdout.on("data", (line) => {
        entry.std.push({ type: "stdout", data: line })
        stdout += line
    })
    handler.stderr.on("data", (line) => entry.std.push({ type: "stderr", data: line }))

    const p = new Promise((resolve) => {
        handler.on("close", (data) => {
            entry.code = data.code
            resolve(undefined)
        })
        handler.on("error", (err) => {
            entry.err = err
            resolve(undefined)
        })
    })

    await handler.spawn()
    await p

    return { stdout, code: entry.code }

}