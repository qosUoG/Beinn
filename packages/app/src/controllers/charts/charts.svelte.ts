
import { log_controller } from "$controllers/log.svelte";
import type { ChartConfigs, ChartMessages } from "./types";





export class Chart<T extends ChartConfigs = ChartConfigs> {
    worker: Worker

    // is_drawing_points
    #is_drawing_points = $state(false)

    get is_drawing_points() {
        return this.#is_drawing_points
    }
    set is_drawing_points(value: boolean) {
        this.#is_drawing_points = value
        this.worker.postMessage({ command: "set_is_drawing_points", payload: { is_drawing_points: value } } satisfies ChartMessages)
    }

    // width and height
    top: number = $state(8)
    left: number = $state(8)
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

    #resize(width: number, height: number) {
        this.worker.postMessage({ command: "resize", payload: { width, height } } satisfies ChartMessages)
    }

    config: T

    showing = $state(true)

    constructor(config: T) {
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


        if (this.worker === undefined) log_controller.appendError(`Worker script of ${config.type} is undefined`)

        this.setConfig(config)
    }

    setConfig(config: T) {
        this.worker.postMessage({ command: "set_config", payload: { config } } satisfies ChartMessages)
    }

    setCanvas(canvas: OffscreenCanvas) {
        this.worker.postMessage({ command: "set_canvas", payload: { canvas, width: this.#width - 16, height: this.#height - 48 } } satisfies ChartMessages, [canvas])
    }

    unsetCanvas() {
        this.worker.postMessage({ command: "unset_canvas" } satisfies ChartMessages)
    }




}