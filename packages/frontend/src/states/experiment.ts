import type { ChartConfigs } from "$components/modules/charts/type"
import type { Experiment } from "qoslab-shared"

export type RuntimeExperiment = Experiment & {
    chart_configs: Record<string, ChartConfigs>

    status: "initial" | "starting" | "started" | "pausing" | "paused" | "continuing" | "continued" | "stopping" | "stopped" | "completed"

    iteration_count: number
    proposed_total_iterations?: number

    total_time: number
    iteration_time_start: number
    timer?: Timer



    ws?: WebSocket

}

export type CreatedRuntimeExperiment = Extract<RuntimeExperiment, { created: true }>

export function getExperimentEventFn(experiment: CreatedRuntimeExperiment) {

    function updateEventFromWsFn(event: MessageEvent<string>) {

        console.log("hi")

        let res:
            { key: "iteration_count", value: number } |
            { key: "proposed_total_iterations", value: number }
            | { key: "status", value: "started" | "paused" | "continued" | "completed" | "initial" | "stopped" }
            | { key: "chart_config", value: ChartConfigs }

        try {
            res = JSON.parse(event.data)
        } catch (e) {
            throw Error("Experiment Event Failed to parse. \nError:\n" + e)
        }

        console.log(res)

        // Reset iteration time only if iteration count is different, and when the expeirment is running 
        if (res.key === "iteration_count" && res.value !== experiment.iteration_count && experiment.status !== "stopped" && experiment.status !== "completed" && experiment.status !== "paused")
            experiment.iteration_time_start = experiment.total_time


        // Pleasing the type checker
        if (res.key !== "chart_config") {
            if (typeof res.value === "number")
                experiment[res.key] = res.value
            else if (typeof res.value === "string")
                experiment[res.key] = res.value
        }


        // Handling status 
        switch (res.key) {
            case "status": {
                switch (res.value) {
                    case "started":
                        experiment.total_time = 0
                        experiment.iteration_time_start = 0
                        experiment.timer = setInterval(() => {
                            experiment.total_time += 1
                        }, 1000)
                        break
                    case "continued":
                        // reset iteration time
                        experiment.iteration_time_start = experiment.total_time
                        experiment.timer = setInterval(() => {
                            experiment.total_time += 1
                        }, 1000)
                        break
                    case "paused":
                    case "completed":
                    case "stopped":
                        clearInterval(experiment.timer)
                        break
                }
                break
            }
            case "chart_config": {
                experiment.chart_configs[res.value.title] = res.value
            }
        }




    }

    return updateEventFromWsFn
}