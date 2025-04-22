
import type { ChartConfigs, ChartWebWorkerMessage } from './charts/chart_types'
import XY_Worker from './charts/xy/worker.js?worker'




export class ChartClass<T extends ChartConfigs = ChartConfigs> {
    private config: T
    get title() {
        return this.config.title
    }
    private experiment_id: string
    private worker: Worker
    private _is_drawing_points = $state(false)
    get is_drawing_points() {
        return this._is_drawing_points
    }

    constructor(config: T, experiment_id: string) {
        this.config = config
        this.experiment_id = experiment_id



        // Create the worker script
        switch (config._type) {
            case "chart:xy": this.worker = new XY_Worker()
        }

        this.worker.postMessage({
            type: "instantiate", payload: {
                id: this.experiment_id, config
            }
        } satisfies ChartWebWorkerMessage)
    }

    set_canvas(payload: Extract<ChartWebWorkerMessage, { type: "set_canvas" }>["payload"]) {
        this.worker.postMessage({ type: "set_canvas", payload } satisfies ChartWebWorkerMessage, [payload.canvas])
    }

    resize(payload: Extract<ChartWebWorkerMessage, { type: "resize" }>["payload"]) {
        this.worker.postMessage({ type: "resize", payload } satisfies ChartWebWorkerMessage)
    }

    reset() {
        this.worker.postMessage({ type: "reset" } satisfies ChartWebWorkerMessage)
    }

    enable_draw_points() {
        this._is_drawing_points = true
        this.worker.postMessage({ type: "enable_draw_points" } satisfies ChartWebWorkerMessage)
    }

    disable_draw_points() {
        this._is_drawing_points = false
        this.worker.postMessage({ type: "disable_draw_points" } satisfies ChartWebWorkerMessage)
    }
    kill() {
        this.worker.postMessage({ type: "kill" } satisfies ChartWebWorkerMessage)
    }


}

export class Charts {
    charts: Record<string, ChartClass> = $state({})


    instantiate(config: ChartConfigs, experiment_id: string) {
        // Only create new item if it does not exist
        if (this.charts[config.title] === undefined)
            this.charts[config.title] = new ChartClass(config, experiment_id)
        else
            this.charts[config.title].reset()
    }



}
