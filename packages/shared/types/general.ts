import type { AllParamTypes } from "./params"

export type EEType = "equipment" | "experiment"

export type ModuleCls = {
    module: string,
    cls: string
}

type Params = Record<string, AllParamTypes>

type EENotCreated = {
    created: false
    id: string
    // created in the python qoslabapp?
    // If created, the module and cls would be defined
    // the params would be collected as well
    module_cls: ModuleCls
}

type EECreated = {
    created: true
    id: string

    module_cls: ModuleCls

    name: string

    params: Params
    temp_params: Params
}

export type Equipment = EENotCreated | EECreated



export type Experiment = EENotCreated | EECreated & {
    charts: Record<string, ChartConfigs>

    running: boolean
    paused: boolean
    completed: boolean

    loop_count: number

    ws?: WebSocket

    // Initial(Stopped):running: false, paused: false, completed: false
    // Start:           running: true,  paused: false, completed: false
    // Pause:           running: true,  paused: true,  completed: false
    // Continue:        running: true,  paused: false, completed: false
    // Complete:        running: false, paused: false, completed: true
    // Stopped(Initial):running: false, paused: false, completed: false
}

export type CreatedExperiment = Extract<Experiment, { created: true }>

export function getUpdateLoopCountFromWsMessageFn(experiment: CreatedExperiment) {

    function updateLoopCountFromWsMessage(event: MessageEvent<string>) {
        console.log(event.data)
        const res = JSON.parse(event.data) as { loop_count: number }
        experiment.loop_count = res.loop_count
    }

    return updateLoopCountFromWsMessage
}

export enum ExperimentStatus {
    NotCreated,
    Stopped,
    Started,
    Paused,
    Completed,
}

export function getExperimentStatus(experiment: Experiment) {
    if (!experiment.created) return ExperimentStatus.NotCreated



    if (experiment.paused) return ExperimentStatus.Paused

    if (experiment.completed) return ExperimentStatus.Completed

    if (experiment.running) return ExperimentStatus.Started

    return ExperimentStatus.Stopped
}



export type ChartConfigs = {
    type: "XYPlot",
    title: string,
    x_name: string,
    y_names: string

}

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