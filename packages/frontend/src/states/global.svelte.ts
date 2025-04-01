
import type { Equipment, Directory, Dependency } from "qoslab-shared";
import type { RuntimeExperiment } from "./experiment";



export let gstore: {
    workspace: {
        path: string,
        directory: Directory,
        dependencies: Record<string, Dependency>
        available_equipments: { modules: string[], cls: string }[]
        available_experiments: { modules: string[], cls: string }[]
        connected: boolean
    }
    equipments: Record<string, Equipment>
    experiments: Record<string, RuntimeExperiment>
    mode: "CONFIG" | "EXPERIMENTS",
    logs: Log[]
    command_history: string[],
    log_socket: WebSocket | undefined,




} = $state({
    workspace: {
        path: import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH,
        directory: { files: [], dirs: {} },
        dependencies: {},
        available_equipments: [],
        available_experiments: [],
        connected: false
    },
    equipments: {},
    experiments: {},
    mode: "CONFIG",
    logs: [],
    command_history: [],
    log_socket: undefined,


})

export function resetGstore() {
    gstore.workspace = {
        path: gstore.workspace.path,
        directory: { files: [], dirs: {} },
        dependencies: {},
        available_equipments: [],
        available_experiments: [],
        connected: false
    }
    gstore.equipments = {}
    gstore.experiments = {}
    gstore.mode = "CONFIG"
    gstore.logs = gstore.logs.filter(l => l.source === "backend")

}

export type Save = {

    dependencies: typeof gstore.workspace.dependencies,
    equipments: typeof gstore.equipments,
    experiments: typeof gstore.experiments,


}







export type Log = {
    source: "backend" | "qoslabapp" | "equipment",
    timestamp: number,
    content: string
}