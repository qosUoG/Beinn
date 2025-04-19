import { Command } from "@tauri-apps/plugin-shell";
import { gstore } from "./global.svelte";



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

    handler.stdout.on("data", async (message) => {
        await gstore.logs.push([
            { source: "beinn", timestamp: Date.now(), content: message }
        ])
    })
    handler.stderr.on("data", async (message) => {
        await gstore.logs.push([
            { source: "beinn", timestamp: Date.now(), content: message }
        ])
    })
    await handler.spawn()
    await p
}


export async function timeoutLoop(timeout_ms: number, fn: () => Promise<boolean> | void) {
    const timenow = Date.now();
    while (Date.now() - timenow <= timeout_ms && await fn()) { }
}

export async function retryOnError(timeout_ms: number, fn: () => Promise<void> | void) {
    await timeoutLoop(
        timeout_ms,
        async () => {
            try {
                // Fetch experiment and equipment
                await fn();
            } catch (error) {
                return true
            }
            return false
        }
    )
}

export function capitalise(input: string) { return input[0].toUpperCase() + String(input).slice(1); }