
import { log_controller } from "$controllers/log.svelte";
import type { ChartConfigs, ChartMessages } from "./types";

export const DEFAULT_WIDTH = 560
export const DEFAULT_HEIGHT = 400



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
    top: number
    left: number
    #width = $state(DEFAULT_WIDTH)
    #height = $state(DEFAULT_HEIGHT)
    canvas_width_offset = 32
    canvas_height_offset = 48
    get width() {
        return this.#width
    }
    set width(value: number) {
        this.#width = value
        this.#resize(value - this.canvas_width_offset, this.#height - this.canvas_height_offset)
    }
    get height() {
        return this.#height
    }
    set height(value: number) {
        this.#height = value
        this.#resize(this.#width - this.canvas_width_offset, value - this.canvas_height_offset)
    }
    get canvas_width() {
        return this.#width - this.canvas_width_offset
    }
    get canvas_height() {
        return this.#height - this.canvas_height_offset
    }

    #resize(width: number, height: number) {
        this.worker.postMessage({ command: "resize", payload: { width, height } } satisfies ChartMessages)
    }

    config: T

    showing = $state(true)

    constructor(config: T, top: number, left: number) {
        this.config = config
        this.top = $state(top)
        this.left = $state(left)
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
        this.auto_axis = true
        this.tooltip_mode = false
        this.worker.postMessage({ command: "set_config", payload: { config } } satisfies ChartMessages)
    }

    setCanvas(canvas: OffscreenCanvas) {
        this.worker.postMessage({ command: "set_canvas", payload: { canvas, width: this.#width - this.canvas_width_offset, height: this.#height - this.canvas_height_offset } } satisfies ChartMessages, [canvas])
    }

    unsetCanvas() {
        this.worker.postMessage({ command: "unset_canvas" } satisfies ChartMessages)
    }

    zoom(direction: "in" | "out", x?: number, y?: number) {
        this.worker.postMessage({ command: "zoom", payload: { direction, x, y } } satisfies ChartMessages)
    }

    pan(old_x: number, old_y: number, new_x: number, new_y: number) {
        this.worker.postMessage({ command: "pan", payload: { old_x, old_y, new_x, new_y } } satisfies ChartMessages)
    }

    #auto_axis = $state(true)
    get auto_axis() {
        return this.#auto_axis
    }
    set auto_axis(value: boolean) {
        this.#auto_axis = value
        if (value)
            this.worker.postMessage({ command: "auto_axis" } satisfies ChartMessages)
    }

    #tooltip_mode = $state(false)
    get tooltip_mode() {
        return this.#tooltip_mode
    }
    set tooltip_mode(value: boolean) {
        this.#tooltip_mode = value
        if (!value)
            this.worker.postMessage({ command: "disable_tooltip" } satisfies ChartMessages)
    }
    enableTooltip(x: number, y: number) {
        this.worker.postMessage({ command: "enable_tooltip", payload: { x, y } } satisfies ChartMessages)
    }

}