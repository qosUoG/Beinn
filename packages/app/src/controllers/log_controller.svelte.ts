type LogEntry = {
    timestamp: number,
    message: string
}

class LogController {
    log_entries: LogEntry[] = $state([])


    append(message: string) {
        this.log_entries.push({ timestamp: Date.now(), message })

        if (this.log_entries.length > 1000) this.log_entries.shift()
    }

    clearLogs() {
        this.log_entries = []
    }
}

export const beinn_log_controller = $state(new LogController())

export const conc_log_controller = $state(new LogController())

