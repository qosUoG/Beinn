import type { AllParamTypes } from "./params.svelte.js"













// export interface Directory {
//     files: string[],
//     dirs: Record<string, Directory>
// }



/* Result Type */
export type Err = {
    type: "APPLICATION" | "USER"
    error: string
}

export function userError(error: string) {
    return { type: "USER", error } satisfies Err
}

export function applicationError(error: string) {
    return { type: "APPLICATION", error } satisfies Err
}

export type Result = {
    success: true,
    value?: any
} | {
    success: false,
    err: Err
}

export function isErr(obj: any): obj is Err {
    return "type" in obj && (obj.type === "APPLICATION" || obj.type === "USER")
}

