
import type { ChartConfigs, ChartMessages } from "./types";





export class Chart<T extends ChartConfigs = ChartConfigs> {
    worker: Worker

    // Worker interface
    #setIsDrawingPoints(value: boolean) {
        this.worker.postMessage({ command: "set_is_drawing_points", payload: { is_drawing_points: value } } satisfies ChartMessages)
    }

    #resize(width: number, height: number) {
        this.worker.postMessage({ command: "resize", payload: { width, height } } satisfies ChartMessages)
    }

    hide() {
        this.worker.postMessage({ command: "hide" } satisfies ChartMessages)
    }


    #is_drawing_points = $state(false)

    get is_drawing_points() {
        return this.#is_drawing_points
    }
    set is_drawing_points(value: boolean) {
        this.#is_drawing_points = value
        this.#setIsDrawingPoints(value)
    }
    #width = $state(560)
    #height = $state(400)
    get width() {
        return this.#width
    }
    set width(value: number) {
        this.#width = value
        this.#resize(value - 16, this.#height - 48)
    }
    get height() {
        return this.#height
    }
    set height(value: number) {
        this.#height = value
        this.#resize(this.#width - 16, value - 48)
    }

    top: number = $state(8)
    left: number = $state(8)


    config: T

    #showing = $state(true)

    get showing() {
        return this.#showing
    }
    set showing(value: boolean) {
        this.#showing = value
        if (value === false) {
            this.hide()
            return
        }
        // reset the chart
        this.reset()
    }


    constructor(config: T, experiment_name: string
    ) {
        this.config = config
        switch (config.type) {
            case "chart:scatter": {
                this.worker = new Worker(new URL("./scatter/worker.js", import.meta.url), { type: "module" })
                this.worker.onmessage = (e) => {
                    console.log(e.data)
                }
                this.worker.onerror = (e) => {
                    console.log(e)
                }
                this.worker.onmessageerror = (e) => {
                    console.log(e)
                }
                break
            }
        }


        if (this.worker === undefined) throw Error(`Worker script of ${config.type} is undefined`)
        this.worker.postMessage({
            command: "instantiate",
            payload: {
                experiment_name, config
            }
        } satisfies ChartMessages)
    }

    setCanvas(canvas: OffscreenCanvas) {

        this.worker.postMessage({ command: "set_canvas", payload: { canvas, width: this.#width - 16, height: this.#height - 48 } } satisfies ChartMessages, [canvas])
    }



    reset() {
        this.worker.postMessage({ command: "reset" } satisfies ChartMessages)
    }


}