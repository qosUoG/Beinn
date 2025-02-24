
import type { Equipment, Experiment, Directory } from "./types/general";

export let gstore:
    {
        project: {
            path: string,
            directory: Directory,
        }
        equipments: Record<string, Equipment>
        experiments: Record<string, Experiment>
        mode: "CONFIG" | "EXPERIMENT",

    } = $state({
        project: {
            path: import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH,
            directory: { files: [], dirs: {} },
        },
        equipments: {},
        experiments: {},
        mode: "CONFIG",
    })
