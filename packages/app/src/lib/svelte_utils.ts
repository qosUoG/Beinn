import type { LogController } from "$controllers/log.svelte"
import { Command } from "@tauri-apps/plugin-shell"

export async function shell({ fn, cmd, cwd, logger }: { fn: string, cmd: string, cwd: string, logger: LogController }) {

    try {

        const handler = Command.create(
            fn, cmd.split(" "), {
            encoding: "utf8",
            cwd
        })
        const p = new Promise((resolve) => {
            handler.on("close", resolve)
            handler.on("error", resolve)
        })

        logger.append(`    ${fn} ${cmd}\n    cwd: ${cwd}`)

        handler.stdout.on("data", (message) => { logger.append("        " + message) })
        handler.stderr.on("data", (message) => { logger.append("        " + message) })

        await handler.spawn()
        await p
        return { success: true }
    } catch (e) {
        logger.append(`    ERROR: ${e}`)
        return { success: false }
    }
}