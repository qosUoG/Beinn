import type { ScatterConfig } from "./scatter/scatter"


export type ChartConfigs = ScatterConfig

export type ChartMessages =
    {
        command: "instantiate"
        payload: {
            config: ChartConfigs
        }
    } |
    {
        command: "set_canvas",
        payload: {
            canvas: OffscreenCanvas,
            width: number,
            height: number
        }
    } | {
        command: "resize",
        payload: { width: number, height: number }
    }
    | { command: "set_is_drawing_points", payload: { is_drawing_points: boolean } }
    | { command: "destroy", payload?: undefined }
    | { command: "hide", payload?: undefined }
    | { command: "show", payload?: undefined }
    | { command: "restart", payload?: undefined }