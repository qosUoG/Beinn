


import { Workspace } from "./workspace";


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
    private _logs: Log[] = $state([])
    get logs() {
        return this._logs
    }

    push(logs: Log[]) {
        this._logs.push(...logs)
    }
}

class GlobalStore {
    accessor mode: AppMode = $state(AppMode.Configuration)

    readonly workspace: Workspace = $state(new Workspace())


    readonly logs: Logs = $state(new Logs())
    private _command_history: string[] = $state([])

    get command_history() {
        return this._command_history
    }

}

export const gstore = new GlobalStore()
