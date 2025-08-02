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

    total_time: number
    total_time_timer: Timer | undefined

    loop_time: number
    loop_time_timer: Timer | undefined

    expected_loop_count: number
}>



export class ExperimentController extends EEBaseController<Experiment> {

    start(name: string) {
        workspace_controller.sendCommand("experiment:start", { name })
    }

    pause(name: string) {
        workspace_controller.sendCommand("experiment:pause", { name })
    }

    stop(name: string) {
        workspace_controller.sendCommand("experiment:stop", { name })
    }

    continue(name: string) {
        workspace_controller.sendCommand("experiment:continue", { name })
    }

    constructor() {
        super("experiment", (instance) => ({
            ...instance,
            temp_params: deepCopy(instance.params),
            status: "initial",
            charts: {},
            loop_count: -1,
            total_time: -1,
            loop_time: -1,
            total_time_timer: undefined,
            loop_time_timer: undefined,
            expected_loop_count: -1,
        }))


        workspace_controller.registerCallback("experiment:status", ({ name, status }: { name: string, status: "started" | "loop_start" | "paused" | "stopped" | "completed" }) => {

            // Handle timer
            switch (status) {
                case "started":
                    this.instances[name].total_time = 0

                    if (this.instances[name].total_time_timer !== undefined)
                        clearInterval(this.instances[name].total_time_timer)

                    this.instances[name].total_time_timer = setInterval(() => {
                        this.instances[name].total_time += 1
                    }, 1000)
                    break
                case "loop_start":
                    this.instances[name].loop_time = 0

                    if (this.instances[name].loop_time_timer !== undefined)
                        clearInterval(this.instances[name].loop_time_timer)

                    this.instances[name].loop_time_timer = setInterval(() => {
                        this.instances[name].loop_time += 1
                    }, 1000)

                    // Restart total time timer in case of coming from paused
                    if (this.instances[name].total_time_timer === undefined)
                        this.instances[name].total_time_timer = setInterval(() => {
                            this.instances[name].total_time += 1
                        }, 1000)
                    break

                case "paused":
                case "stopped":
                case "completed":
                    clearInterval(this.instances[name].total_time_timer)
                    clearInterval(this.instances[name].loop_time_timer)
            }

            // Handle status
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

        workspace_controller.registerCallback("experiment:expected_loop_count", ({ name, loop_count }: { name: string, loop_count: number }) => {
            this.instances[name].expected_loop_count = loop_count
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