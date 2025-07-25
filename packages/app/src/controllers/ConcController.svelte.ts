import { LogController } from "./LogController.svelte";

class ConcController extends LogController {
    constructor() {
        super();

    }

    command_history: string[] = []
    query_list_cache: string[] = []
    query_index = -1
    original_query = ""


    getEarlierQuery() {
        if (this.query_index < this.query_list_cache.length - 1)
            this.query_index += 1
        return this.query_list_cache[this.query_index]
    }

    getLaterQuery() {
        if (this.query_index >= 0)
            this.query_index -= 1

        if (this.query_index < 0) {
            return this.original_query
        }
        return this.query_list_cache[this.query_index]
    }

    updateQuery(query: string) {
        this.original_query = query
        if (query === "") {
            this.query_list_cache = this.command_history
            return
        }
        this.query_list_cache = this.command_history.filter((c) => c.startsWith(query))
    }

    send(command: string) {
        this.command_history.unshift(command);
        this.updateQuery("");
        //TODO: send command to backend
    }


}

export const conc_controller = $state(new ConcController());