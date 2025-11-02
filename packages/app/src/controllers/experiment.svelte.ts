import { deepCopy, shell, type Prettify } from "$lib/utils"
import { Command } from "@tauri-apps/plugin-shell"
import { EEBaseController, Instance, type ConcInstance, type InstanceSave } from "./_ee.svelte"
import { Chart } from "./charts/charts.svelte"
import type { ChartConfigs } from "./charts/types"

import { workspace_controller } from "./workspace.svelte"
import type { AllParamTypes } from "./params.svelte"
import { tick } from "svelte"
import { exists, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"
import { equipment_controller } from "./equipment.svelte"
import { Cli } from "./cli.svelte"

type ExperimentEvent = {
    event: "started"
    expected_loop_count: number
    chart_configs: Record<string, ChartConfigs>
    saver_configs: string[]
} | {
    event: "loop_start"
    loop_count: number
} | {
    event: "paused"
} | {
    event: "ended"
}
class Clock {
    milliseconds: number = $state(0)
    timer: Timer | undefined = undefined
    past_now: number = 0

    start() {
        this.past_now = Date.now()
        this.timer = setInterval(() => {
            const now = Date.now()
            this.milliseconds = now - this.past_now
            this.past_now = now
        }, 500)
    }

    stop() {
        if (this.timer === undefined) return
        this.clearTimer()
        this.milliseconds = Date.now() - this.past_now

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

    current_loop_count: number = $state(0)
    expected_loop_count: number = $state(-1)

    total_time_clock: Clock = $state(new Clock())
    loop_time_clock: Clock = $state(new Clock())

    loop_count: number = $state(0)

    ws: WebSocket | undefined = undefined

    note: string | undefined = $state(undefined)
    sidetab_showing: "cli" | "notes" = $state("cli")

    cli: Cli = $state(new Cli())



    async start() {
        new WebSocket("ws://localhost:8080/close")
        this.state = "starting"
        const handler = Command.create("uv", ["run", "experiment"], { cwd: workspace_controller.path! })


        handler.stdout.on("data", (line) => {
            if (line.startsWith("ws:loaded")) {
                this.startWebsocket()
                console.log("started")
                return
            }
            console.log(line)
            this.cli.logs.append(line)
        })
        handler.stderr.on("data", (line) => {
            console.log(line)
            this.cli.logs.append(line)
        })

        const p = new Promise((resolve) => {
            handler.on("close", resolve)
            handler.on("error", resolve)
        })

        await handler.spawn()
        await p
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
                case "started":
                    this.expected_loop_count = data.expected_loop_count

                    for (const config of Object.values(data.chart_configs)) {

                        if (this.charts[config.title] !== undefined) {
                            this.charts[config.title].reset()
                            return
                        }
                        const chart = new Chart(config)
                        this.charts[config.title] = chart
                    }

                    if (data.saver_configs.length > 0)
                        this.note = ""
                    break
                case "loop_start":
                    this.state = "looping"
                    this.current_loop_count = data.loop_count
                    break
                case "paused":
                    this.state = "paused"
                    break
                case "ended":
                    this.state = "ready"
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