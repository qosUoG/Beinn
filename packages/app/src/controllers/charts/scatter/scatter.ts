


export interface ScatterConfig {
    type: "chart:scatter"
    title: string
    x_axis: string,
    y_axis: string,
    y_names: string[]
    mode: "overwrite" | "append",
}

// export type ChartWebWorkerMessage =
//     {
//         type: "instantiate"

//         payload: {
//             id: string,
//             config: XYChartConfig
//         }
//     } |
//     {

//         type: "set_canvas",
//         payload: {
//             canvas: OffscreenCanvas,
//             width: number,
//             height: number
//         }
//     } | {
//         type: "resize",
//         payload: { width: number, height: number }
//     } | {
//         type: "reset"
//     } | {
//         type: "enable_draw_points"
//     } | {
//         type: "disable_draw_points"
//     } | {
//         type: "kill"
//     }
