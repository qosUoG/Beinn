import type { ChartConfiguration } from "chart.js"

export type XYChartMode = "overwrite" | "append"

export type XYChartConfig = {
    type: "XYPlot"
    title: string
    x_axis: string,
    y_axis: string,
    y_names: string[]
    mode: XYChartMode
}


export type XYWebWorkerMessage = {
    type: "instantiate",
    payload: {
        canvas: OffscreenCanvas,
        id: string,
        config: XYChartConfig
        width: number,
        height: number
    }
} | {
    type: "resize",
    payload: { width: number, height: number }
}


