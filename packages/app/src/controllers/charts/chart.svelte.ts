
import { log_controller } from "$controllers/log.svelte";
import type { ChartConfig, fromWorkerChartMessages, toWorkerChartMessages } from "./types";

export const DEFAULT_WIDTH = 560
export const DEFAULT_HEIGHT = 400



export class Chart {
    worker: Worker

    // is_drawing_points
    #is_drawing_points = $state(false)

    get is_drawing_points() {
        return this.#is_drawing_points
    }
    set is_drawing_points(value: boolean) {
        this.#is_drawing_points = value
        this.worker.postMessage({ command: "set_is_drawing_points", payload: { is_drawing_points: value } } satisfies toWorkerChartMessages)
    }

    // width and height
    element: HTMLDivElement | undefined = $state(undefined)
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
        this.worker.postMessage({ command: "resize", payload: { width, height } } satisfies toWorkerChartMessages)
    }

    showing = $state(true)

    config: ChartConfig

    constructor(config: ChartConfig, top: number, left: number, onWsClose: (chart: Chart) => void) {
        this.top = $state(top)
        this.left = $state(left)
        this.config = $state(config)


        this.worker = new Worker(new URL("./scatter/worker.js", import.meta.url), { type: "module" })
        this.worker.onmessage = (e) => {
            const res = e.data as fromWorkerChartMessages
            switch (res.command) {
                case "error": {
                    console.log(res.payload.error)
                    break
                }
                case "ws_closed": {
                    onWsClose(this)
                    break
                }
            }
        }
        this.worker.onerror = console.log
        this.worker.onmessageerror = console.log
        this.worker.postMessage({ command: "set_config", payload: { config } } satisfies toWorkerChartMessages)
        this.worker.postMessage({ command: "x_key", payload: { x_key: config.columns[0]! } } satisfies toWorkerChartMessages)
        this.auto_axis = true
        this.tooltip_mode = false
    }

    zoom(direction: "in" | "out", x?: number, y?: number) {
        this.worker.postMessage({ command: "zoom", payload: { direction, x, y } } satisfies toWorkerChartMessages)
    }

    pan(old_x: number, old_y: number, new_x: number, new_y: number) {
        this.worker.postMessage({ command: "pan", payload: { old_x, old_y, new_x, new_y } } satisfies toWorkerChartMessages)
    }

    #auto_axis = $state(true)
    get auto_axis() {
        return this.#auto_axis
    }
    set auto_axis(value: boolean) {
        this.#auto_axis = value
        if (value)
            this.worker.postMessage({ command: "auto_axis" } satisfies toWorkerChartMessages)
    }

    #tooltip_mode = $state(false)
    get tooltip_mode() {
        return this.#tooltip_mode
    }
    set tooltip_mode(value: boolean) {
        this.#tooltip_mode = value
        if (!value)
            this.worker.postMessage({ command: "disable_tooltip" } satisfies toWorkerChartMessages)
    }
    enableTooltip(x: number, y: number) {
        this.worker.postMessage({ command: "enable_tooltip", payload: { x, y } } satisfies toWorkerChartMessages)
    }

    onMount(canvas: OffscreenCanvas) {
        this.worker.postMessage({ command: "mount", payload: { canvas, width: this.#width - this.canvas_width_offset, height: this.#height - this.canvas_height_offset } } satisfies toWorkerChartMessages, [canvas])
    }

    onUnmount() {
        this.worker.postMessage({ command: "unmount" } satisfies toWorkerChartMessages)
    }

    wsOpen() {
        this.worker.postMessage({ command: "ws_open" } satisfies toWorkerChartMessages)
    }

    destroy() {
        this.worker.postMessage({ command: "ws_close" } satisfies toWorkerChartMessages)
        this.worker.postMessage({ command: "destroy" } satisfies toWorkerChartMessages)
    }
}