import type { ChartConfiguration } from "chart.js"

export type XYEvent = {
    type: "instantiate",
    payload: {
        canvas: OffscreenCanvas,
        overwrite: boolean
        url: string,
        config: {
            x_name: string,
            y_names: string[]
        }
    }
}

// Numbers are in 
export type XYFrame = Record<string, number>