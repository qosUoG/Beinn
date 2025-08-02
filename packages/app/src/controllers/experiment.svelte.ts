import { deepCopy, type Prettify } from "$lib/utils"
import { Chart } from "./charts/charts.svelte"
import type { ChartConfigs } from "./charts/types"
import { EEBaseController, type Instance } from "./eebase.svelte"
import { workspace_controller } from "./workspace.svelte"

export type Experiment = Prettify<Instance & {
    status:
    "initial" |
    "started" |
    "running" |
    "pausing" |
    "paused" |
    "stopping" |
    "stopped" |
    "completed",

    charts: Record<string, Chart>

    loop_count: number
}>



export class ExperimentController extends EEBaseController<Experiment> {

    start(name: string) {
        workspace_controller.sendCommand("experiment:start", { name, })
    }

    constructor() {
        super("experiment", (instance) => ({ ...instance, temp_params: deepCopy(instance.params), status: "initial", charts: {}, loop_count: -1 }))

        workspace_controller.registerCallback("experiment:status", ({ name, status }: { name: string, status: "started" | "loop_start" | "paused" | "stopped" | "completed" }) => {
            switch (status) {
                case "started":
                case "paused":
                case "stopped":
                case "completed":
                    this.instances[name].status = status
                    break
                case "loop_start":
                    this.instances[name].status = "running"
                    break

            }
        })


        workspace_controller.registerCallback("experiment:loop_count", ({ name, loop_count }: { name: string, loop_count: number }) => {
            this.instances[name].loop_count = loop_count
        })

        workspace_controller.registerCallback("experiment:chart_config", ({ name, config }: { name: string, config: ChartConfigs }) => {
            this.instances[name].charts[config.title] = new Chart(config, name)
        })
    }

}

export const experiment_controller = $state(new ExperimentController())