import { deepCopy, type Prettify } from "$lib/utils"
import { Command } from "@tauri-apps/plugin-shell"
import { EEBaseController, type ConcInstance } from "./_ee.svelte"
import { Chart } from "./charts/charts.svelte"
import type { ChartConfigs } from "./charts/types"

import { workspace_controller } from "./workspace.svelte"
import { beinn_log_controller } from "./log.svelte"
import type { AllParamTypes } from "./params.svelte"




export class ExperimentController extends EEBaseController {

    module: string = $state("")
    cls: string = $state("")
    params: Record<string, AllParamTypes> = $state({})

    param_opens: boolean = $state(true)
    composite_opens: Record<string, boolean> = $state({})


    status:
        "undefined" |
        "initial" |
        "started" |
        "running" |
        "pausing" |
        "paused" |
        "stopping" |
        "stopped" |
        "completed" = $state("undefined")

    charts: Record<string, Chart> = $state({})
    loop_count: number = $state(0)

    total_time: number = $state(-1)
    total_time_timer: Timer | undefined = $state(undefined)
    total_time_timer_timestamp: number = $state(0)

    loop_time: number = $state(-1)
    loop_time_timer: Timer | undefined = $state(undefined)
    loop_time_timer_timestamp: number = $state(0)

    expected_loop_count: number = $state(-1)

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


    get closeable() {

        if (this.status !== "completed" && this.status !== "stopped" && this.status !== "initial")
            return false

        return true
    }

    constructor() {
        super("experiment");

        // setTimeout(() => {


        //     workspace_controller.registerCallback("experiment:status", ({ name, status }: { name: string, status: "started" | "loop_start" | "paused" | "stopped" | "completed" }) => {

        //         // Handle loop count
        //         if (status === "started") {
        //             this.instances[name].loop_count = 0
        //         }

        //         // Handle timer
        //         const updateTotalTime = () => {
        //             const now = Date.now()
        //             this.instances[name].total_time += now - this.instances[name].total_time_timer_timestamp
        //             this.instances[name].total_time_timer_timestamp = now
        //         }

        //         const updateLoopTime = () => {
        //             const now = Date.now()
        //             this.instances[name].loop_time += now - this.instances[name].loop_time_timer_timestamp
        //             this.instances[name].loop_time_timer_timestamp = now
        //         }


        //         switch (status) {
        //             case "started":
        //                 if (this.instances[name].total_time_timer !== undefined)
        //                     clearInterval(this.instances[name].total_time_timer)

        //                 this.instances[name].total_time = 0
        //                 this.instances[name].total_time_timer_timestamp = Date.now()
        //                 this.instances[name].total_time_timer = setInterval(updateTotalTime, 500)

        //                 this.instances[name].loop_time = -1
        //                 break
        //             case "loop_start":
        //                 if (this.instances[name].loop_time_timer !== undefined) {
        //                     clearInterval(this.instances[name].loop_time_timer)
        //                     updateLoopTime()
        //                 }


        //                 this.instances[name].loop_time = 0
        //                 this.instances[name].loop_time_timer_timestamp = Date.now()


        //                 this.instances[name].loop_time_timer = setInterval(updateLoopTime, 500)

        //                 // Restart total time timer in case of coming from paused
        //                 if (this.instances[name].total_time_timer === undefined) {
        //                     this.instances[name].total_time_timer_timestamp = Date.now()
        //                     this.instances[name].total_time_timer = setInterval(updateTotalTime, 500)
        //                 }
        //                 break

        //             case "paused":
        //             case "stopped":
        //             case "completed":
        //                 if (this.instances[name].total_time_timer !== undefined) {
        //                     clearInterval(this.instances[name].total_time_timer)
        //                     updateTotalTime()
        //                     this.instances[name].total_time_timer = undefined
        //                     this.instances[name].total_time_timer_timestamp = 0
        //                 }
        //                 if (this.instances[name].loop_time_timer !== undefined) {
        //                     clearInterval(this.instances[name].loop_time_timer)
        //                     updateLoopTime()
        //                     this.instances[name].loop_time_timer = undefined
        //                     this.instances[name].loop_time_timer_timestamp = 0
        //                 }



        //         }

        //         // Handle status
        //         switch (status) {
        //             case "started":
        //             case "paused":
        //             case "stopped":
        //             case "completed":
        //                 this.instances[name].status = status
        //                 break
        //             case "loop_start":
        //                 this.instances[name].status = "running"
        //                 break

        //         }
        //     })

        //     workspace_controller.registerCallback("experiment:expected_loop_count", ({ name, expected_loop_count }: { name: string, expected_loop_count: number }) => {
        //         this.instances[name].expected_loop_count = expected_loop_count
        //     })


        //     workspace_controller.registerCallback("experiment:loop_count", ({ name, loop_count }: { name: string, loop_count: number }) => {
        //         this.instances[name].loop_count = loop_count
        //     })

        //     workspace_controller.registerCallback("experiment:chart_config", ({ name, config }: { name: string, config: ChartConfigs }) => {
        //         if (this.instances[name].charts[config.title] !== undefined) {
        //             this.instances[name].charts[config.title].reset()
        //             return
        //         }
        //         const chart = new Chart(config, name)
        //         this.instances[name].charts[config.title] = chart

        //     })

        // })
    }

    async getParams() {
        // Get the default params list of the experiment
        const res = await Command.create(
            "uv",
            ["run", "params", this.module, this.cls]
            , {
                encoding: "utf8",
                cwd: workspace_controller.path!
            }).execute()

        if (res.code !== 0) {
            beinn_log_controller.append(`error while creating equipment with module ${this.module} and class ${this.cls}: ${res.stderr}`)
            return
        }

        console.log(res.stdout)

        const instance = JSON.parse(res.stdout) as ConcInstance

        this.params = instance.params
        this.status = "initial"
    }




}

export const experiment_controller = $state(new ExperimentController())