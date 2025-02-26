
import type { Equipment, Experiment, Directory, Dependency } from "qoslab-shared";

export let gstore:
    {
        workspace: {
            path: string,
            directory: Directory,
            dependencies: Record<string, Dependency>
            available_equipment_paths: string[]
            available_experiment_paths: string[]
        }
        equipments: Record<string, Equipment>
        experiments: Record<string, Experiment>
        mode: "CONFIG" | "EXPERIMENT",


    } = $state({
        workspace: {
            path: import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH,
            directory: { files: [], dirs: {} },
            dependencies: {},
            available_equipment_paths: [],
            available_experiment_paths: [],
        },
        equipments: {},
        experiments: {},
        mode: "CONFIG",
    })
