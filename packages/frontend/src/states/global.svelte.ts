
import type { Equipment, Directory, Dependency } from "qoslab-shared";
import type { RuntimeExperiment } from "./experiment";

export let gstore:
    {
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
        log_socket: WebSocket | undefined


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
        log_socket: undefined
    })

export type Log = {
    source: "backend" | "qoslabapp" | "equipment",
    timestamp: number,
    content: string
}