type LogEntry = {
    timestamp: number,
    message: string
}

export class LogController {
    #log_entries: { value: LogEntry[] } = $state({
        value: [

        ]
    })
    get log_entries() {
        return this.#log_entries.value
    }

    scroll_position: number = $state(0)
    is_refreshing: boolean = $state(true)
    show_timetext: boolean = $state(false)

    append(message: string) {
        this.#log_entries.value.push({ timestamp: Date.now(), message })

        if (this.#log_entries.value.length > 3000) this.#log_entries.value.shift()
    }

    clearLogs() {
        this.#log_entries.value = []
    }
}

export const beinn_log_controller = $state(new LogController())



