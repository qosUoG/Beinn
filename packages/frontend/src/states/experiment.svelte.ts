

import { type ChartConfigs, type EET, type ModuleCls } from "qoslab-shared"
import { tick } from "svelte"
import { gstore, type Availables } from "./global.svelte"
import { EE } from "./ee.svelte"
import { qoslabappContinueExperiment, qoslabappGetAvailableEEs, qoslabappGetExperimentEventsWs, qoslabappPauseExperiment, qoslabappStartExperiment, qoslabappStopExperiment } from "$services/qoslabapp.svelte"
import { getRandomId } from "$lib/utils"
import { Charts } from "./chart.svelte"


export class Experiment extends EE {
    /* Common part of EE */
    constructor(id: string, name?: string) {
        super(id, "experiment", name)

    }

    // Override
    async create() {
        // Create the experiment in qoslabapp and fetch initial params
        await super.create()

        // Start listening to experiment events here
        this.event_ws = qoslabappGetExperimentEventsWs({
            id: this.id,
            onmessage: (event: MessageEvent<string>) => {
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

                switch (res.key) {
                    case "iteration_count":
                        // Reset iteration time only if iteration count is different, and when the experiment is running 
                        if (res.value !== this._iteration_count && this._status !== "stopped" && this._status !== "completed" && this._status !== "paused")
                            this._iteration_time_start = this._total_time

                        this._iteration_count = res.value
                        break
                    case "proposed_total_iterations":
                        this._proposed_total_iterations = res.value
                        break
                    case "status":
                        this._status = res.value

                        switch (res.value) {
                            case "started":
                                this._total_time = 0
                                this._iteration_time_start = 0
                                this.timer = setInterval(() => {
                                    this._total_time += 1
                                }, 1000)
                                break
                            case "continued":
                                // reset iteration time
                                this._iteration_time_start = this._total_time
                                this.timer = setInterval(() => {
                                    this._total_time += 1
                                }, 1000)
                                break
                            case "paused":
                            case "completed":
                            case "stopped":
                                clearInterval(this.timer)
                                break
                        }
                        break

                    case "chart_config":
                        this._charts.instantiate(res.value)
                        break
                }
            },
        });
    }



    /*Experiment Specific */
    private _charts: Charts = $state(new Charts())
    get charts() {
        return this._charts
    }
    private _status: ExperimentStatus = $state("initial")
    get status() {
        return this._status
    }

    private _iteration_count: number = $state(-1)
    get iteration_count() {
        return this._iteration_count
    }
    private _proposed_total_iterations: number | undefined = $state()
    get proposed_total_iterations() {
        return this._proposed_total_iterations
    }
    proposedIterationsIsInfinit() {
        return this._proposed_total_iterations === -1
    }

    private _total_time: number = $state(0)
    get total_time() {
        return this._total_time
    }

    private _iteration_time_start: number = $state(0)
    get iteration_time_start() {
        return this._iteration_time_start
    }

    private event_ws: WebSocket | undefined = $state()
    private timer: Timer | undefined = $state()

    async start() {
        this._iteration_count = -1;
        this._status = "starting";

        // Reset the charts
        Object.values(this.charts).forEach(cs => { cs.reset() });

        await tick();
        await qoslabappStartExperiment({ id: this.id });
    }

    async pause() {
        this._status = "pausing";
        await qoslabappPauseExperiment({ id: this.id });
    }
    async stop() {
        this._status = "stopping";
        await qoslabappStopExperiment({ id: this.id });
    }
    async continue() {
        this._status = "continuing";
        await qoslabappContinueExperiment({ id: this.id });

    }

    isRunnable() {
        return this._created &&
            this.name.length > 0 &&
            JSON.stringify(this.params) ===
            JSON.stringify(this.temp_params) &&
            this.params !== undefined
    }

}

export type ExperimentStatus =
    "initial" |
    "starting" |
    "started" |
    "pausing" |
    "paused" |
    "continuing" |
    "continued" |
    "stopping" |
    "stopped" |
    "completed"


export class Experiments {
    private _experiments: Record<string, Experiment> = $state({})
    get experiments() {
        return this._experiments
    }

    private _available_module_cls: Availables = $state([])

    async instantiate(payload?: { id?: string, name?: string }) {
        let id: string | undefined, name: string | undefined
        if (payload) {
            id = payload.id
            name = payload.name
        }

        if (!id) id = getRandomId(Object.keys(this._experiments))
        const new_experiment = new Experiment(id, name)
        this._experiments[id] = new_experiment

        await tick()
        $effect(() => {
            const shall_delete = new_experiment.shall_delete

            if (shall_delete)
                delete this._experiments[id]
        })

        return new_experiment
    }

    moduleClsValid(module_cls: ModuleCls) {
        return this._available_module_cls.find(({ modules, cls }) =>
            modules.includes(module_cls.module) && module_cls.cls === cls
        ) !== undefined
    }


    toSave: () => EET[] = () => {
        return Object.values(this._experiments).map(e => e.toSave())
    }


    refreshAvailables = async () => {
        this._available_module_cls = await qoslabappGetAvailableEEs("experiment", { prefixes: gstore.workspace.dependencies.prefixes })
    }

    get available_module_cls() {
        return this._available_module_cls
    }

    runnables = $derived(
        Object.values(this.experiments.experiments).filter(e => e.isRunnable())

    );

    getInstanceables(id: string) {
        return Object.values(this._experiments)
            // Split here for type check sake
            .filter((e) => e.created)
            // Name needs to be defiend
            .filter((e) => e.id !== id && e.name && e.name.length > 0)
            .map((e) => ({ key: e.name, value: e.id }))

    }

}



