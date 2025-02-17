import type { Directory } from "shared-types";


export let gstore:
    {
        workspace: {
            path: string,
            directory: Directory,
        }
        experiment: {
            path: string
        },
        mode: "CONFIG" | "EXPERIMENT",

    } = $state({
        workspace: {
            path: import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH,
            directory: { files: [], dirs: {} },
        },
        experiment: {
            path: ""
        },
        mode: "CONFIG",
    })
