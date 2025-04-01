
import type { Equipment, Directory, Dependency } from "qoslab-shared";
import type { RuntimeExperiment } from "./experiment";

export const gstore_template: {
    workspace: {
        path: string,
        directory: Directory,
        dependencies: Record<string, Dependency>
        available_equipments: { modules: string[], cls: string }[]
        available_experiments: { modules: string[], cls: string }[]
    }
    equipments: Record<string, Equipment>
    experiments: Record<string, RuntimeExperiment>
    mode: "CONFIG" | "EXPERIMENTS",
    logs: Log[]
    command_history: string[],
    log_socket: WebSocket | undefined,
    workspace_connected: boolean


} = {
    workspace: {
        path: import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH,
        directory: { files: [], dirs: {} },
        dependencies: {},
        available_equipments: [],
        available_experiments: [],
    },
    equipments: {},
    experiments: {},
    mode: "CONFIG",
    logs: [],
    command_history: [],
    log_socket: undefined,
    workspace_connected: false
}

export let gstore: {
    workspace: {
        path: string,
        directory: Directory,
        dependencies: Record<string, Dependency>
        available_equipments: { modules: string[], cls: string }[]
        available_experiments: { modules: string[], cls: string }[]
    }
    equipments: Record<string, Equipment>
    experiments: Record<string, RuntimeExperiment>
    mode: "CONFIG" | "EXPERIMENTS",
    logs: Log[]
    command_history: string[],
    log_socket: WebSocket | undefined,
    workspace_connected: boolean


} = $state({
    workspace: {
        path: import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH,
        directory: { files: [], dirs: {} },
        dependencies: {},
        available_equipments: [],
        available_experiments: [],
    },
    equipments: {},
    experiments: {},
    mode: "CONFIG",
    logs: [],
    command_history: [],
    log_socket: undefined,
    workspace_connected: false
})

export function resetGstore() {
    gstore.workspace = {
        path: gstore.workspace.path,
        directory: { files: [], dirs: {} },
        dependencies: {},
        available_equipments: [],
        available_experiments: [],
    }
    gstore.equipments = {}
    gstore.experiments = {}
    gstore.mode = "CONFIG"
    gstore.logs = gstore.logs.filter(l => l.source === "backend")


    gstore.workspace_connected = false
}







export type Log = {
    source: "backend" | "qoslabapp" | "equipment",
    timestamp: number,
    content: string
}