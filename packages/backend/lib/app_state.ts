import type { Subprocess } from "bun"

export let app_state: {
    workspace: {
        path: string
        dependencies: string[],
    },
    pyproc: Subprocess | undefined
} = {
    workspace: {
        path: "",
        dependencies: [],
    },
    pyproc: undefined
}