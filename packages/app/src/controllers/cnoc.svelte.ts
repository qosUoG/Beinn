import { equipment_controller } from "./equipment.svelte";
import { LogController } from "./log.svelte";
import { workspace_controller } from "./workspace.svelte";

class CnocController extends LogController {
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
        this.append(command);
        // Check if the command is an equipment code
        for (const name of Object.keys(equipment_controller.instances)) {
            if (command.match(name)) {
                workspace_controller.sendCommand("interpret:equipment", { code: command, name });
                return
            }
        }

        workspace_controller.sendCommand("interpret:general", { code: command });
    }


}

export const cnoc_controller = $state(new CnocController());