import { deepCopy, type Prettify } from "$lib/utils"
import { dependency_controller } from "./DependencyController.svelte"
import { EEBaseController, type Instance } from "./EEBaseController.svelte"
import { beinn_log_controller } from "./LogController.svelte"
import type { AllParamTypes } from "./Params.svelte"
import { workspace_controller } from "./WorkspaceController.svelte"



export type Experiment = Instance

export class ExperimentController extends EEBaseController {

    constructor() {
        super("experiment")
    }
}

export const experiment_controller = $state(new ExperimentController())