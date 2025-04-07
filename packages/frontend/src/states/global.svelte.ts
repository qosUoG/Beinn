import { Workspace } from "./workspace.svelte";


export enum AppMode {
    Configuration,
    Runtime
}

export type Availables = { modules: string[], cls: string }[]



export type Log = {
    source: "backend" | "qoslabapp" | "equipment",
    timestamp: number,
    content: string
}

class Logs {
    logs: Log[] = $state([])


    push(logs: Log[]) {
        this.logs.push(...logs)
    }
}

class GlobalStore {
    mode: AppMode = $state(AppMode.Configuration)
    workspace: Workspace = $state(new Workspace())
    logs: Logs = $state(new Logs())
    command_history: string[] = $state([])
}

export const gstore = $state(new GlobalStore())
