import type { AllParamTypes } from "./params"

export interface Experiment {
    id: string
    name?: string
    path?: string,
    params?: Record<string, AllParamTypes>
    temp_params?: Record<string, AllParamTypes>
}

export interface Equipment {
    id: string
    name?: string
    path?: string,
    params?: Record<string, AllParamTypes>
    temp_params?: Record<string, AllParamTypes>
}

export interface Directory {
    files: string[],
    dirs: Record<string, Directory>
}

export interface Dependency {
    id: string
    source: {
        type: "git",
        git: string,
        subdirectory: string,
    } | {
        type: "path",
        path: string
        directory: Directory,
    } | {
        type: "pip"
    }

    name?: string,
    fullname?: string,

    confirmed: boolean
}