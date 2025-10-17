import { deepCopy, shell, type Prettify } from "$lib/utils"
import { Command } from "@tauri-apps/plugin-shell"
import { EEBaseController, Instance, type ConcInstance, type InstanceSave } from "./_ee.svelte"
import { Chart } from "./charts/charts.svelte"
import type { ChartConfigs } from "./charts/types"

import { workspace_controller } from "./workspace.svelte"
import type { AllParamTypes } from "./params.svelte"
import { tick } from "svelte"
import { exists, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"




export class Experiment extends Instance {

    constructor(module: string, cls: string) {
        super(module, cls)
    }

    status:
        "ready" |
        "starting" |
        "looping" |
        "pausing" |
        "paused" |
        "stopping" = $state("ready")

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
        // workspace_controller.sendCommand("start", {})
    }

    pause() {
        // workspace_controller.sendCommand("pause", {})
    }

    stop() {
        // workspace_controller.sendCommand("stop", {})
    }

    continue() {
        // workspace_controller.sendCommand("continue", {})
    }






    // constructor() {
    //     super("experiment");

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
    // }



}


export class ExperimentController extends EEBaseController {

    module: string = $state("")
    cls: string = $state("")

    experiment: Experiment | undefined = $state(undefined)

    get editable() {
        return this.experiment === undefined || this.experiment.status === "ready"
    }

    constructor() { super("experiment") }

    async loadExperiment() {
        const experiment: Experiment = new Experiment(this.module, this.cls)
        await experiment.initialize()

        this.experiment = experiment
    }

    async save() {
        await writeTextFile(workspace_controller.path! + "/.beinn/experiment.json",
            JSON.stringify(this.experiment?.toSave()))
    }

    async loadSave(path: string) {
        if (!await exists(path + "/.beinn/experiment.json")) return
        const save = JSON.parse(await readTextFile(path + "/.beinn/experiment.json")) as InstanceSave | undefined

        if (save === undefined) return


        // Check if save is included in the imports
        const found = this.imports.find(imp => imp.module === save.module && imp.cls === save.cls)
        if (found === undefined) return

        this.module = save.module
        this.cls = save.cls
        await tick()

        // Create the experiment
        await this.loadExperiment()

        // Apply the save
        this.experiment!.assignParams(save.params)
        this.experiment!.param_opens = save.param_opens
        for (const key of Object.keys(save.composite_opens))
            if (key in this.experiment!.composite_opens)
                this.experiment!.composite_opens = save.composite_opens

    }

    reset() {
        this.experiment = undefined
        this.imports = []
        this.module = ""
        this.cls = ""
    }
}
export const experiment_controller = $state(new ExperimentController())