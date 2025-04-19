


import { tick } from "svelte"
import { gstore, type Availables } from "./global.svelte"
import { EE, type EET } from "./ee.svelte"
import { meallContinueExperiment, meallGetAvailableEEs, meallGetExperimentEventsWs, meallPauseExperiment, meallStartExperiment, meallStopExperiment } from "$lib/meall.svelte"
import { getRandomId } from "$lib/utils"
import { Charts, type ChartConfigs } from "./chart.svelte"
import { toastApplicationError } from "$components/modules/ToastController.svelte"
import type { ModuleCls } from "./dependency.svelte"



export class Experiment extends EE {
    /* Common part of EE */
    constructor(id: string, name?: string) {
        super(id, "experiment", name)

    }

    // Override
    async create() {
        // Create the experiment in meall and fetch initial params
        await super.create()

        // Start listening to experiment events here
        this.event_ws = meallGetExperimentEventsWs({
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
                    toastApplicationError(`Experiment ${this.id} failed to parse event with data ${event.data} Error: ${e}`)
                    return
                }

                switch (res.key) {
                    case "iteration_count":
                        // Reset iteration time only if iteration count is different, and when the experiment is running 
                        if (res.value !== this._iteration_count && this._status !== "stopped" && this._status !== "completed" && this._status !== "paused")
                            this._iteration_time_start = Date.now()

                        this._iteration_count = res.value
                        break
                    case "proposed_total_iterations":
                        this._proposed_total_iterations = res.value
                        break
                    case "status":
                        this._status = res.value

                        switch (res.value) {
                            case "started":
                                const now = Date.now()
                                this._total_time_start = now
                                this._iteration_time_start = now

                                break
                            case "continued":
                                // reset iteration time
                                this._iteration_time_start = Date.now()

                                break
                            case "paused":
                            case "completed":
                            case "stopped":
                                break

                        }
                        break

                    case "chart_config":
                        this._charts.instantiate(res.value, this.id)
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

    private _total_time_start: number = $state(Date.now())
    get total_time_start() {
        return this._total_time_start
    }

    private _iteration_time_start: number = $state(Date.now())
    get iteration_time_start() {
        return this._iteration_time_start
    }

    private event_ws: WebSocket | undefined = $state()


    async start() {
        this._iteration_count = -1;
        this._status = "starting";

        // Reset the charts
        Object.values(this._charts.charts).forEach(cs => { cs.reset() });

        await tick();
        await meallStartExperiment({ id: this.id });
    }

    async pause() {
        this._status = "pausing";
        await meallPauseExperiment({ id: this.id });
    }
    async stop() {
        this._status = "stopping";
        await meallStopExperiment({ id: this.id });
    }
    async continue() {
        this._status = "continuing";
        await meallContinueExperiment({ id: this.id });

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

    instantiate(payload?: { id?: string, name?: string }) {
        let id: string | undefined, name: string | undefined
        if (payload) {
            id = payload.id
            name = payload.name
        }

        if (!id) id = getRandomId(Object.keys(this._experiments))
        const new_experiment = new Experiment(id, name)
        this._experiments[id] = new_experiment

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
        this._available_module_cls = await meallGetAvailableEEs("experiment", { prefixes: gstore.workspace.dependencies?.prefixes ?? [] })
    }

    get available_module_cls() {
        return this._available_module_cls
    }



    getInstanceables(id: string) {
        return Object.values(this._experiments)
            // Split here for type check sake
            .filter((e) => e.created)
            // Name needs to be defiend
            .filter((e) => e.id !== id && e.name && e.name.length > 0)
            .map((e) => ({ key: e.name, value: e.id }))

    }

}



