import { log_controller } from "$controllers/log.svelte"
import { Command } from "@tauri-apps/plugin-shell"

export async function shell({ fn, cmd, description, cwd }:
    { fn: string, cmd: string | string[], description: string, cwd: string }) {
    const entry = log_controller.appendShell({
        cwd,
        command: fn + " " + (typeof cmd === "string" ? cmd : cmd.join(" ")),
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