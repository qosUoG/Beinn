import type { AllParamTypes } from "./params"

export type ModuleCls = {
    module: string,
    cls: string
}

export type Experiment = {
    created: false
    id: string
    // created in the python qoslabapp?
    // If created, the module and cls would be defined
    // the params would be collected as well
    module_cls: ModuleCls
} | {
    created: true
    id: string

    module_cls: ModuleCls

    name: string

    params: Record<string, AllParamTypes>
    temp_params: Record<string, AllParamTypes>
}

export type Equipment = Experiment

export interface Directory {
    files: string[],
    dirs: Record<string, Directory>
}

export type Dependency = {
    id: string
    confirmed: false
} | {
    id: string
    source: DependencySource

    name: string,
    fullname: string,

    confirmed: true
}

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