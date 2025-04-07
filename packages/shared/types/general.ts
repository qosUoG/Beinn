import type { AllParamTypes } from "./params"

export type ModuleCls = {
    module: string,
    cls: string
}

// Only types that cross boundary of backend and frontend would be here
export type DependencySource = {
    type: "git",

    git: string,
    subdirectory: string,
    branch: string
} | {
    type: "path",

    path: string,
    editable: boolean
} | {
    type: "pip",

    package: string
} | {
    type: "local",

    directory: string
}

export function sourceEqual(a: DependencySource, b: DependencySource) {
    if (a.type !== b.type) return false

    switch (a.type) {
        case "local":
            return a.directory === (b as Extract<DependencySource, { type: "local" }>).directory
        case "git":
            return a.git === (b as Extract<DependencySource, { type: "git" }>).git
        case "path":
            return a.path === (b as Extract<DependencySource, { type: "path" }>).path
        case "pip":
            return a.package === (b as Extract<DependencySource, { type: "pip" }>).package
    }
}

export type DependencyT_YetInstalled = {
    installed: false
    source: DependencySource
}

export type DependencyT_Installed = {
    installed: true
    source: DependencySource


    name: string,
    fullname: string,
}

export type DependencyT = DependencyT_YetInstalled | DependencyT_Installed



/* EE Base Type */
export type EEType = "equipment" | "experiment"

export type EET = {
    id: string
    created: boolean
    module_cls: ModuleCls

    // The following may exist even created
    // This is because the EE may be in save but failed to setup when loading workspace
    name: string
    params: Record<string, AllParamTypes>
    temp_params: Record<string, AllParamTypes>
}


export type Save = {
    dependencies: DependencyT[],
    experiments: EET[],
    equipments: EET[],
}


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

