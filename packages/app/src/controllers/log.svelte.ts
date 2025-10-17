import type { Prettify } from "$lib/utils"

type BaseEntry = {
    timestamp: number,
}

export type ErrorEntry = Prettify<BaseEntry & {
    type: "error",
    message: string
}>


export type ShellEntry = Prettify<BaseEntry & {
    type: "shell",
    description: string,
    cwd: string,
    command: string,
    std: { type: "stdout" | "stderr", data: string }[],
    err: string,
    code: number | null
}>

export type LogEntry = ErrorEntry | ShellEntry


export class LogController {
    #log_entries: LogEntry[] = $state([])
    get log_entries() {
        return this.#log_entries
    }

    // scroll_position: number = $state(0)
    // is_refreshing: boolean = $state(true)

    reset() {
        this.#log_entries = []
        // this.scroll_position = 0
        // this.is_refreshing = true
    }

    appendError(message: string) {
        this.#log_entries.push({ message, type: "error", timestamp: Date.now() })
    }

    appendShell(entry: Omit<ShellEntry, "timestamp" | "type">) {
        const ent = { ...entry, type: "shell", timestamp: Date.now() } as ShellEntry
        this.#log_entries.push(ent)
        return ent
    }
}

export const log_controller = $state(new LogController())



