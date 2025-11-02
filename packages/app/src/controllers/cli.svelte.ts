import { deepCopy } from "$lib/utils";


class Logs {
    entries: string[] = $state([])

    append(entry: string) {
        this.entries.push(entry)
    }

    clear() {
        this.entries = []
    }
}

class History {
    // FILO 
    history: string[] = []

    search_cache: string[] = []
    search_index: number = -1

    #query: string = ""
    get query() {
        return this.#query
    }

    set query(value: string) {
        this.#query = value

        // Reset the search
        if (value === "") {
            this.search_cache = deepCopy(this.history)
            this.search_index = -1
            return
        }

        this.search_cache = this.history.filter((c) => c.startsWith(value))
        this.search_index = 0
    }

    add(entry: string) {
        this.history.unshift(entry)
    }

    clear() {
        this.history = []
        this.search_cache = []
        this.search_index = -1
        this.#query = ""
    }

    getPrev() {
        if (this.search_index === -1) return ""

        // Set the search index to the lower index
        this.search_index -= 1

        // Return to the whole history
        if (this.search_index === -1) {
            this.query = ""
            return ""
        }

        return this.search_cache[this.search_index]

    }

    getNext() {
        if (this.search_index < this.search_cache.length - 1)
            this.search_index += 1

        return this.search_cache[this.search_index]
    }
}

export class Cli {
    history: History = $state(new History())
    logs: Logs = $state(new Logs())

    follow_scroll: boolean = $state(true)
    small_scroll_height: number = $state(0)
    large_scroll_height: number = $state(0)

    #command: string = $state("")

    get command() {
        return this.#command
    }

    set command(value: string) {
        this.#command = value
        this.history.query = value
    }

    prev() {
        this.#command = this.history.getPrev()
    }

    next() {
        this.#command = this.history.getNext()
    }

    clear() {
        this.logs.clear()
        this.history.clear()
        this.#command = ""
    }

    record() {
        const res = this.#command
        this.history.add(this.#command);
        this.logs.append(this.#command);
        this.command = "";
        return res;
    }


}

