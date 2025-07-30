
import ScatterWorker from "./scatter/worker.js?worker";
import type { ChartConfigs, ChartMessages } from "./types";





export class Chart<T extends ChartConfigs> {
    worker: Worker

    // Worker interface
    #setIsDrawingPoints(value: boolean) {
        this.worker.postMessage({ command: "set_is_drawing_points", payload: { is_drawing_points: value } } satisfies ChartMessages)
    }

    #resize(width: number, height: number) {
        this.worker.postMessage({ command: "resize", payload: { width, height } } satisfies ChartMessages)
    }


    #is_drawing_points = $state(false)

    get is_drawing_points() {
        return this.#is_drawing_points
    }
    set is_drawing_points(value: boolean) {
        this.#is_drawing_points = value
        this.#setIsDrawingPoints(value)
    }
    #width = $state(300)
    #height = $state(200)
    get width() {
        return this.#width
    }
    set width(value: number) {
        this.#width = value
        this.#resize(value, this.#height)
    }
    get height() {
        return this.#height
    }
    set height(value: number) {
        this.#height = value
        this.#resize(this.#width, value)
    }


    config: T


    constructor(config: T, experiment_name: string, worker_init: typeof ScatterWorker
    ) {
        this.config = config
        this.worker = new worker_init()

        this.worker.postMessage({
            command: "instantiate",
            payload: {
                experiment_name, config
            }
        } satisfies ChartMessages)
    }

    setCanvas(canvas: OffscreenCanvas) {
        this.worker.postMessage({ command: "set_canvas", payload: { canvas, width: this.#width, height: this.#height } } satisfies ChartMessages)
    }


}