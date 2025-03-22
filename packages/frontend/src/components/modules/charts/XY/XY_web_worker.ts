import { Chart, type ChartConfiguration, type Point } from "chart.js/auto";
import type { XYChartConfig, XYEvent, XYFrame } from "./XY_types";


let chart: Chart
let ws: WebSocket

// Webworker onmessage
onmessage = function (event: MessageEvent<XYEvent>) {
    switch (event.data.type) {
        case "instantiate":

            const { canvas, url, mode, config: { x_axis, y_axis, y_names } } = event.data.payload

            const config: ChartConfiguration = {
                type: "line",
                data: {
                    // start blank
                    datasets: []
                },
                options: {
                    animation: false,
                    parsing: false,

                    scales: {
                        x: {
                            type: "linear",
                            title: { text: x_axis, display: true }
                        },
                        y: {
                            type: "linear",
                            title: { text: y_axis, display: true }
                        }
                    }
                }
            }

            // Push empty arrays as placeholders
            y_names.forEach(y_name => {
                config.data.datasets.push({ data: [], label: y_name })
            })

            chart = new Chart(canvas, config)



            // Establish websocket to get data
            ws = new WebSocket(url)

            if (ws === null) throw Error("Websocket connection failed!")

            ws.onmessage = getWsOnmessageHandler(y_names.length, mode)


    }
}

// WebSocket onmessage
const getWsOnmessageHandler = (y_length: number, mode: XYEvent["payload"]["mode"]) => {

    function onmessage(event: MessageEvent<{ frames: XYFrame[] }>) {
        const frames = event.data.frames

        // Frame size is assumed to be right, as such only size of the first frame is checked
        if (frames[0].length !== y_length + 1) throw Error("Frame size does not match with the config of the chart")

        const chart_data = chart.data

        switch (mode) {
            case "overwrite": {
                // In overwrite mode

                // frames are first sorted by it's x value
                frames.sort((a, b) => a[0] - b[0])

                // append frame in reversed order, skip if repeated
                const x_set = new Set<number>()
                // Sort the y dataset if that data is added to that y 
                const y_set = new Set<number>()
                for (let frame_index = frames.length; frame_index > 0; frame_index--) {
                    const frame = frames[frame_index]

                    const x = frame[0]

                    // put x into set to avoid repeat
                    if (x_set.has(x)) continue
                    else x_set.add(x)

                    // Put each non null y value into dataset
                    for (let y_index = 1; y_index < frame.length; y_index++) {
                        const y = frame[y_index]
                        if (y === null) continue

                        // add y to dataset that needs sorted
                        y_set.add(y_index);

                        // Check if a point with same x already exist
                        const point_index = chart_data.datasets[y_index].data.findIndex(point => (point as Point).x === x);

                        // -1 if not found
                        if (point_index === -1)
                            chart_data.datasets[y_index].data.push({ x, y })
                        else
                            (chart_data.datasets[y_index].data[point_index] as Point).y = y
                    }
                }

                // sort the datasets required
                y_set.forEach(y_index => {
                    (chart_data.datasets[y_index].data as Point[]).sort((a, b) => a.x - b.x)
                })


                break
            }
            case "append": {
                // In append mode, x is assumed to be in ascending order without repeat

                // Frame size is assumed to be right, as such only size of the first frame is checked
                if (frames[0].length !== y_length + 1) throw Error("Frame size does not match with the config of the chart")

                // append y value to each dataset
                frames.forEach(frame => {
                    const x = frame[0]

                    for (let y_index = 1; y_index < frame.length; y_index++) {
                        const y = frame[y_index]
                        if (y === null) continue

                        chart_data.datasets[y_index].data.push({ x, y })
                    }
                })


                break
            }
        }

        // update the chart!
        chart.update()


    }

    return onmessage
}