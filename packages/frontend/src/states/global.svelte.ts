import { tick } from "svelte";
import { Workspace } from "./workspace.svelte";


export type AppMode = "Configuration" | "Runtime"


export type Availables = { modules: string[], cls: string }[]



export type Log = {
    source: "beinn" | "python" | "equipment"
    timestamp: number,
    content: string
}

class Logs {
    readonly logs: Log[] = $state([])
    async push(logs: Log[]) {
        if (this.logs.length + logs.length > 5000)
            this.logs.splice(logs.length - 5000, logs.length)
        await tick()
        this.logs.push(...logs)

    }
}

class GlobalStore {
    mode: AppMode = $state("Configuration")
    readonly workspace: Workspace = $state(new Workspace())
    readonly logs: Logs = $state(new Logs())
    readonly command_history: string[] = $state([])
}

export const gstore = $state(new GlobalStore())
