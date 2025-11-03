import type { ScatterConfig } from "./scatter/scatter"


export type ChartConfigs = ScatterConfig

export type ChartMessages =
    | { command: "set_config", payload: { config: ChartConfigs } }
    | { command: "set_canvas", payload: { canvas: OffscreenCanvas, width: number, height: number } }
    | { command: "unset_canvas", payload?: undefined }
    | { command: "resize", payload: { width: number, height: number } }
    | { command: "set_is_drawing_points", payload: { is_drawing_points: boolean } }
    | { command: "zoom", payload: { direction: "in" | "out", x?: number, y?: number } }
    | { command: "pan", payload: { old_x: number, old_y: number, new_x: number, new_y: number } }
    | { command: "auto_axis", payload?: undefined }
    | { command: "enable_tooltip", payload: { x: number, y: number } }
    | { command: "disable_tooltip", payload?: undefined }


