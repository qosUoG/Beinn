import { Chart, type ChartConfiguration } from "chart.js/auto";
import type { XYEvent, XYFrame } from "./XY_types";


let chart: Chart
let ws: WebSocket

let x_values: number[]
let y_values: number[][]

onmessage = function (event: MessageEvent<XYEvent>) {
    switch (event.data.type) {
        case "instantiate":

            const { canvas, url, overwrite, config: { x_name, y_names } } = event.data.payload



            const config: ChartConfiguration = {
                type: "line",
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    animation: false
                }
            }

            chart = new Chart(canvas, config)



            // Establish websocket to get data
            ws = new WebSocket(url)

            if (ws === null) return

            ws.onmessage = (event: MessageEvent<{ frames: XYFrame[] }>) => {
                const frames = event.data.frames

                const chart_data = chart.data

                // In overwrite mode
                if (overwrite) {
                    frames.forEach((frame) => {
                        // Check if the new value of x_name already exist
                        if (chart.data.l frame[x_name] )


                })



            }
    }
}
}