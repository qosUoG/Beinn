import type { ChartConfiguration } from "chart.js"

export type XYChartConfig = {
    type: "xy"
    x_axis: string,
    y_axis: string,
    y_names: string[]
}

export type XYEvent = {
    type: "instantiate",
    payload: {
        canvas: OffscreenCanvas,
        mode: "overwrite" | "append"
        url: string,
        config: XYChartConfig
    }
}

// Numbers are in 
export type XYFrame = number[]