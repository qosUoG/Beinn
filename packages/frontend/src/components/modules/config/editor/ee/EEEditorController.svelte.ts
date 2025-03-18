import type { EEType } from "qoslab-shared";

export let eeeditor: { mode: EEType, id?: string } = $state({
    mode: "equipment",
    id: undefined
})