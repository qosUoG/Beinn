import type { Directory } from "shared-types";
import type { AllParamTypes } from "./types/params";



export interface Experiment {
    id: string
    name?: string
    path?: string,
    params?: Record<string, AllParamTypes>
}

export interface Equipment {
    id: string
    name?: string
    path?: string,
    params?: Record<string, AllParamTypes>
}

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
