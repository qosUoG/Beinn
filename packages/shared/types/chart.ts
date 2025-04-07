export type XYChartMode = "overwrite" | "append"

export type XYChartConfig = {
    type: "XYPlot"
    title: string
    x_axis: string,
    y_axis: string,
    y_names: string[]
    mode: XYChartMode,
}

export type ChartConfigs = XYChartConfig