import { deepCopy, type Prettify } from "$lib/utils"
import { Command } from "@tauri-apps/plugin-shell"
import { EEBaseController, type ConcInstance } from "./_ee.svelte"
import { Chart } from "./charts/charts.svelte"
import type { ChartConfigs } from "./charts/types"

import { workspace_controller } from "./workspace.svelte"
import { beinn_log_controller } from "./log.svelte"
import type { AllParamTypes } from "./params.svelte"
import { tick } from "svelte"




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

    start() {
        workspace_controller.sendCommand("start", {})
    }

    pause() {
        workspace_controller.sendCommand("pause", {})
    }

    stop() {
        workspace_controller.sendCommand("stop", {})
    }

    continue() {
        workspace_controller.sendCommand("continue", {})
    }


    get closeable() {
        return !(this.status !== "completed" && this.status !== "stopped" && this.status !== "initial" && this.status !== "undefined")
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
            beinn_log_controller.append(`error while creating experiment with module ${this.module} and class ${this.cls}: ${res.stderr}`)
            return
        }
        const instance = JSON.parse(res.stdout) as ConcInstance

        this.composite_opens = {}
        await tick()

        for (const [key, value] of Object.entries(instance.params))
            if (value.type === "composite" && this.composite_opens[key] === undefined)
                this.composite_opens[key] = true

        this.params = instance.params
        this.status = "initial"

        await tick()

    }




}

export const experiment_controller = $state(new ExperimentController())