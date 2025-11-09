import { deepCopy, shell, sleep, type Prettify } from "$lib/utils"
import { Child, Command } from "@tauri-apps/plugin-shell"
import { EEBaseController, Instance, type ConcInstance, type InstanceSave } from "./_ee.svelte"
import { Chart } from "./charts/chart.svelte"
import type { ChartConfigs } from "./charts/types"

import { workspace_controller } from "./workspace.svelte"
import { save2Runtime, type AllParamTypes, type RuntimeAllParamTypes } from "./params.svelte"
import { tick } from "svelte"
import { exists, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"
import { equipment_controller } from "./equipment.svelte"
import { Cli } from "./cli.svelte"
import { log_controller } from "./log.svelte"

type ExperimentEvent = {
    event: "loop_start"
    loop_count: number
} | {
    event: "paused"
} | {
    event: "ended"
    loop_ended: boolean
}
class Clock {
    milliseconds: number = $state(0)
    timer: Timer | undefined = undefined
    past_now: number = 0

    get stopped() {
        return this.timer === undefined
    }

    start() {
        this.past_now = Date.now()
        this.timer = setInterval(() => {
            const now = Date.now()
            this.milliseconds += now - this.past_now
            this.past_now = now
        }, 500)
    }

    stop() {
        if (this.timer === undefined) return

        this.clearTimer()
        this.milliseconds += Date.now() - this.past_now

    }

    clearTimer() {

        if (this.timer === undefined) return

        clearInterval(this.timer)
        this.timer = undefined
    }

    reset() {
        this.milliseconds = 0
        this.clearTimer()
    }

    restart() {
        this.reset()
        this.start()
    }
}


export class Experiment extends Instance {

    constructor(module: string, cls: string) {
        super(module, cls)
    }

    state:
        "ready" |
        "starting" |
        "looping" |
        "pausing" |
        "paused" |
        "stopping" = $state("ready")

    charts: Record<string, Chart> = $state({})
    chart_in_focus: string | undefined = $state(undefined)

    loop_count: number = $state(0)
    expected_loop_count: number = $state(-1)

    total_time_clock: Clock = $state(new Clock())
    loop_time_clock: Clock = $state(new Clock())

    starting_time_total: number | undefined = $state(undefined)

    ws: WebSocket | undefined = undefined

    note: string | undefined = $state(undefined)

    cli: Cli = $state(new Cli())

    process: Child | undefined = undefined

    async start() {
        this.total_time_clock.reset()
        this.loop_time_clock.reset()
        this.starting_time_total = undefined

        this.cli.clear()

        if (this.ws !== undefined) this.ws.close(4000)
        new WebSocket("ws://localhost:8080/close")


        if (this.process) this.process.kill()

        this.total_time_clock.start()
        this.state = "starting"
        const handler = Command.create("uv", ["run", "experiment"], { cwd: workspace_controller.path! })


        handler.stdout.on("data", (line) => {
            try {
                let raw = JSON.parse(line)
                if (raw.event === "started") {
                    let { expected_loop_count, chart_configs, saver_configs } = raw as
                        {
                            event: "started"
                            expected_loop_count: number
                            chart_configs: Record<string, ChartConfigs>
                            saver_configs: string[]
                        }
                    this.expected_loop_count = expected_loop_count

                    let top = 16
                    let left = 16
                    let names: Set<string> = new Set()

                    for (const config of Object.values(chart_configs)) {
                        if (names.has(config.title)) {
                            this.cli.logs.append(`ERROR:Chart with title ${config.title} already exists`)
                        }
                        names.add(config.title)

                        if (this.charts[config.title] !== undefined) {
                            this.charts[config.title].setConfig(config)
                            top += 8
                            left += 8
                            continue
                        }

                        this.charts[config.title] = new Chart(config, top, left)
                        top += 8
                        left += 8
                    }

                    if (saver_configs.length > 0)
                        this.note = ""
                    this.startWebsocket()
                    return
                }
            } catch (e) {
                this.cli.logs.append(line)
                return
            }



            this.cli.logs.append(line)
        })
        handler.stderr.on("data", (line) => {
            this.cli.logs.append(line)
        })

        handler.on("error", (e) => {
            console.log("Python process error: " + e)
            this.cli.logs.append(e)
        })

        handler.on("close", ({ code }) => {
            console.log("Python process exited with code" + { code })
            this.loop_time_clock.stop()
            this.total_time_clock.stop()
            this.state = "ready"
        })


        this.process = await handler.spawn()



    }

    pause() {
        this.state = "pausing"
        this.ws!.send(JSON.stringify({ event: "pause" }))
    }

    stop() {
        this.state = "stopping"
        this.ws!.send(JSON.stringify({ event: "stop" }))
    }

    continue() {
        this.ws!.send(JSON.stringify({ event: "continue" }))
    }

    saveNote(note: string) {
        this.ws!.send(JSON.stringify({ event: "save_note", value: note }))
        this.note = note
    }

    interpret() {
        if (this.cli.command === "") return

        const command = this.cli.record();

        // Check if the command is an equipment code
        for (const name of equipment_controller.equipment_names) {
            if (command.match(name)) {
                this.ws!.send(JSON.stringify({ event: "interpret", value: { command, name } }))
                return
            }
        }

        this.ws!.send(JSON.stringify({ event: "interpret", value: { command } }))
    }

    startWebsocket() {
        this.ws = new WebSocket("ws://localhost:8080/experiment")

        this.ws.onopen = () => {
            this.ws!.send(JSON.stringify({
                event: "start",
                value: {
                    equipments: Object.values(equipment_controller.equipments).map(e => ({
                        name: e.name,
                        module: e.module,
                        cls: e.cls,
                        params: e.params,
                    })),
                    experiment: {
                        module: this.module,
                        cls: this.cls,
                        params: this.params,
                    },
                }
            }))
        }

        this.ws.onmessage = (e) => {

            const data = JSON.parse(e.data) as ExperimentEvent

            switch (data.event) {

                case "loop_start":
                    if (this.starting_time_total === undefined)
                        this.starting_time_total = this.total_time_clock.milliseconds

                    if (this.total_time_clock.stopped)
                        this.total_time_clock.start()

                    this.loop_time_clock.restart()


                    this.state = "looping"
                    this.loop_count = data.loop_count
                    break
                case "paused":
                    this.state = "paused"
                    this.loop_time_clock.stop()
                    this.total_time_clock.stop()
                    break
                case "ended":
                    this.state = "ready"
                    this.loop_time_clock.stop()
                    this.total_time_clock.stop()

                    if (data.loop_ended)
                        this.loop_count += 1


                    break
            }
        }
    }

}


export class ExperimentController extends EEBaseController {

    module: string = $state("")
    cls: string = $state("")

    experiment: Experiment | undefined = $state(undefined)

    get editable() {
        return this.experiment === undefined || this.experiment.state === "ready"
    }

    get playable() {
        if (this.experiment === undefined || this.experiment.state !== "ready") return false

        function paramIsPlayable(param: RuntimeAllParamTypes) {
            switch (param.type) {
                case "select.float":
                case "select.int":
                    return param.options.includes(param.value)

                case "select.str":
                    return param.options.includes(param.value)

                case "int":
                case "float":
                    return param.value !== undefined
                case "str":
                    return param.value !== "" && param.value !== undefined
                case "bool":
                    return true
                case "instance.equipment":
                    return param.value !== null

            }
        }

        return Object.values(experiment_controller.experiment!.params).every(
            (param) => {
                if (!("type" in param))
                    return Object.values(param).every((p) => paramIsPlayable(p))

                return paramIsPlayable(param as RuntimeAllParamTypes)
            })
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
        this.experiment!.assignParams(save2Runtime(save.params))
        this.experiment!.param_opens = save.param_opens
        for (const key of Object.keys(save.composite_opens))
            if (key in this.experiment!.composite_opens)
                this.experiment!.composite_opens = save.composite_opens

    }

    reset() {
        this.experiment = undefined
        super.reset()
        this.module = ""
        this.cls = ""
    }
}
export const experiment_controller = $state(new ExperimentController())