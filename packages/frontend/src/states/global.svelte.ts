
import type { Equipment, Experiment, Directory } from "qoslab-shared";

export let gstore:
    {
        workspace: {
            path: string,
            directory: Directory,
            dependencies: string[]
        }
        equipments: Record<string, Equipment>
        experiments: Record<string, Experiment>
        mode: "CONFIG" | "EXPERIMENT",

    } = $state({
        workspace: {
            path: import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH,
            directory: { files: [], dirs: {} },
            dependencies: []
        },
        equipments: {},
        experiments: {},
        mode: "CONFIG",
    })
