import { deepCopy, type Prettify } from "$lib/utils"
import { Chart } from "./charts/charts.svelte"
import type { ChartConfigs } from "./charts/types"
import { dependency_controller } from "./DependencyController.svelte"
import { EEBaseController, type Instance } from "./EEBaseController.svelte"
import { beinn_log_controller } from "./LogController.svelte"
import type { AllParamTypes } from "./Params.svelte"
import { workspace_controller } from "./WorkspaceController.svelte"

export type Experiment = Instance



export class ExperimentController extends EEBaseController {
    constructor() {
        super("experiment")

        workspace_controller.registerCallback("experiment:status", ({ name, status }: { name: string, status: "started" | "loop_start" | "paused" | "stopped" | "completed" }) => {
            // TODO
        })

        workspace_controller.registerCallback("experiment:chart_config", ({ name, config }: { name: string, config: ChartConfigs }) => {
            // TODO
        })
    }

    charts: Record<string, Chart> = $state({})
}

export const experiment_controller = $state(new ExperimentController())