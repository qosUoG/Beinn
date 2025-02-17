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
            path: "/Volumes/External/QosLab/example/experiment",
            directory: { files: [], dirs: {} },
        },
        experiment: {
            path: ""
        },
        mode: "CONFIG",
    })
