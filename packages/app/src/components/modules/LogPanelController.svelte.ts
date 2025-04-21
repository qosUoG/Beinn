import { tick } from "svelte"

export type Log_Entry = {
    type: "beinn" | "meall"
    timestamp: number,
    message: string
}

let log_entries: Log_Entry[] = $state([])

export function clearLogs() {
    log_entries = []
}

/**
 * Returns a function that allows appending message to the log entry
 */
export async function pushLog(type: "beinn" | "meall", message: string) {

    const new_log = { type, timestamp: Date.now(), message }
    log_entries.push(new_log)

    await tick()

    // Drop old log if total log exceed 1000 entries
    if (log_entries.length > 5000) log_entries.splice(0, log_entries.length - 1000)

}

export const log_panel = $state({
    show_beinn: true,
    show_meall: true,
    show_time: false,
    show: false,

    get displayingLogs() {
        return log_entries.filter(
            (l) => {
                return (this.show_beinn && l.type === "beinn") || (this.show_meall && l.type === "meall")
            }
        ).sort((a, b) => a.timestamp - b.timestamp);
    }
})

