import type { ChartConfigs, XYChartConfig } from "qoslab-shared"




export type ChartWebWorkerMessage =
    {
        type: "instantiate"

        payload: {
            id: string,
            config: XYChartConfig
        }
    } |
    {

        type: "set_canvas",
        payload: {
            canvas: OffscreenCanvas,
            width: number,
            height: number
        }
    } | {
        type: "resize",
        payload: { width: number, height: number }
    } | {
        type: "reset"
    } | {
        type: "connect_ws"
    } | {
        type: "disconnect_ws"
    }



export class ChartClass<T extends ChartConfigs = ChartConfigs> {
    private config: T
    get title() {
        return this.config.title
    }
    private experiment_id: string
    private worker: Worker
    constructor(config: T, experiment_id: string) {
        this.config = config
        this.experiment_id = experiment_id

        // Create the worker script
        this.worker = new Worker(new URL("./charts/" + config.type + "/worker.js", import.meta.url), {
            type: "module",
        });

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

    connect_ws() {
        this.worker.postMessage({ type: "connect_ws" } satisfies ChartWebWorkerMessage)
    }

    reset() {
        this.worker.postMessage({ type: "reset" } satisfies ChartWebWorkerMessage)
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
