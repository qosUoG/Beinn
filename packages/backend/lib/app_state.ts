import type { Subprocess } from "bun"

export let app_state: {
    pyproc: Subprocess | undefined
} = {
    pyproc: undefined
}