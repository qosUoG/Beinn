import type { EEType } from "$states/ee.svelte";


export let eeeditor: {
    mode: EEType
    , id?: string
} = $state({
    mode: "equipment",
    id: undefined
})