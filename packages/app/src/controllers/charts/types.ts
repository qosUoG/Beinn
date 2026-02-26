


export type ChartConfig = {
    title: string
    columns: string[]
}

export type toWorkerChartMessages =
    | { command: "set_config", payload: { config: ChartConfig } }
    | { command: "xy_axis", payload: { x_axis: string, y_axis: string[] } }
    | { command: "destroy", payload?: undefined }

    | { command: "ws_open", payload?: undefined }
    | { command: "ws_close", payload?: undefined }

    | { command: "mount", payload: { canvas: OffscreenCanvas, width: number, height: number } }
    | { command: "unmount", payload?: undefined }

    | { command: "resize", payload: { width: number, height: number } }

    | { command: "set_is_drawing_points", payload: { is_drawing_points: boolean } }

    | { command: "zoom", payload: { direction: "in" | "out", x?: number, y?: number } }
    | { command: "pan", payload: { old_x: number, old_y: number, new_x: number, new_y: number } }
    | { command: "auto_axis", payload?: undefined }


    | { command: "enable_tooltip", payload: { x: number, y: number } }
    | { command: "disable_tooltip", payload?: undefined }


export type fromWorkerChartMessages =
    | { command: "ws_closed", payload?: undefined }
    | { command: "error", payload: { error: string } }
