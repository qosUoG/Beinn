import { tick } from "svelte"

export type CliEntry = {
    timestamp: number,
    message: string
}

let cli_entries: CliEntry[] = $state([])

export function clearCli() {
    cli_entries = []
}

export async function pushCli(message: string) {

    cli_entries.push({ timestamp: Date.now(), message })

    await tick()

    // Drop old log if total log exceed 1000 entries
    if (cli_entries.length > 1000) cli_entries.splice(0, cli_entries.length - 1000)

}

export const cli_panel = $state({
    show_time: false,
    show: false,
    query: "",
    command_history: [""],
    query_index: 0,

    get cli_entries() {
        return cli_entries
    },

    get query_list() {
        return [""].concat(
            (this.command_history as string[]).filter((c) => c.startsWith(this.query) && c !== this.query))
    },

    updateQuery(input: string) {
        this.query = input;
        this.query_index = 0;
    }


})


