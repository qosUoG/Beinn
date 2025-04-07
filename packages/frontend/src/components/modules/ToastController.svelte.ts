import { getRandomId } from "$lib/utils"
import type { Err } from "qoslab-shared"
import { tick } from "svelte"

export const content: Record<string, string> = $state({})

function displayToast(value: string) {
    const id = getRandomId(Object.keys(content))
    content[id] = value
}

export function toastError(error: Err) {
    displayToast(`${error.type} ERROR: ${error.error}`)
}

export function toastApplicationError(error: string) {
    toastError({ type: "APPLICATION", error })
}

export function toastUnreacheable(location: string) {
    toastApplicationError(`UNREACHEABLE at ${location}`)
}

export function toastUserError(error: string) {
    toastError({ type: "USER", error })
}