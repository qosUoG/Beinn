import { Workspace } from "./workspace.svelte";


export type AppMode = "Configuration" | "Runtime"


export type Availables = { modules: string[], cls: string }[]



export type Log = {
    source: "backend" | "qoslabapp" | "equipment",
    timestamp: number,
    content: string
}

class Logs {
    readonly logs: Log[] = $state([])
    push(logs: Log[]) {
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
