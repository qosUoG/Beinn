import { Chart, type ChartConfiguration, type Point } from "chart.js/auto";
import type { XYWebWorkerMessage, XYChartMode } from "./XY_types";
import { qoslabappWs } from "$services/utils";


let chart: Chart
let canvas: OffscreenCanvas
let ws: WebSocket
let _y_names: string[]

// Webworker onmessage
onmessage = function (event: MessageEvent<XYWebWorkerMessage>) {
    switch (event.data.type) {
        case "instantiate": {
            const { canvas: from_canvas, id, config: { mode, x_axis, y_axis, y_names, title }, width, height } = event.data.payload

            _y_names = y_names

            canvas = from_canvas

            canvas.width = width
            canvas.height = height

            const config: ChartConfiguration = {
                type: "line",
                data: {
                    // start blank
                    datasets: []
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    // resizeDelay: 500,
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
            ws = new WebSocket(qoslabappWs(`chart/${id}/${title}`))

            if (ws === null) throw Error("Websocket connection failed!")

            ws.binaryType = "arraybuffer"

            ws.onmessage = getWsOnmessageHandler(y_names.length, mode)
            break
        }

        case "resize": {
            if (!canvas) return

            const { width, height } = event.data.payload

            canvas.width = width
            canvas.height = height

            chart.resize(width, height - 1)
            break
        }

        case "reset": {
            let new_datasets: { data: Point[], label: string }[] = []
            _y_names.forEach(y_name => {
                new_datasets.push({ data: [], label: y_name })
            })
            chart.data.datasets = new_datasets
            break
        }


    }
}



// WebSocket onmessage
const getWsOnmessageHandler = (y_length: number, mode: XYChartMode) => {

    function onmessage(event: MessageEvent<ArrayBuffer>) {

        const frames_bytes = new DataView(event.data)
        // Frame size is assumed to be right, thus not checked


        function* parseFrames(frames_bytes: DataView<ArrayBuffer>) {
            let offset = 0

            while (offset < frames_bytes.byteLength) {
                // yield frame by frame
                const res: (number | null)[] = [frames_bytes.getFloat64(offset, true)]
                offset += 8
                for (let i = 0; i < y_length; i++) {
                    const has_y = frames_bytes.getFloat64(offset, true)
                    offset += 8

                    if (has_y !== 0) {
                        res.push(has_y ? frames_bytes.getFloat64(offset, true) : null)
                        offset += 8
                    } else
                        res.push(null)
                }
                yield res
            }
        }

        const chart_data = chart.data


        switch (mode) {
            case "overwrite": {
                // In overwrite mode

                // Get all of the frames
                const frames = [...parseFrames(frames_bytes)]

                // Frame size is assumed to be right, as such only size of the first frame is checked
                if (frames[0].length !== y_length + 1) throw Error("Frame size does not match with the config of the chart")


                // frames are first sorted by it's x value
                frames.sort((a, b) => (a[0] as number) - (b[0] as number))

                // append frame in reversed order, skip if repeated
                const x_set = new Set<number>()
                // Sort the y dataset if that data is added to that y 
                const y_set = new Set<number>()
                for (let frame_index = frames.length; frame_index > 0; frame_index--) {
                    const frame = frames[frame_index]

                    const x = frame[0] as number

                    // put x into set to avoid repeat
                    if (x_set.has(x)) continue
                    else x_set.add(x)

                    // Put each non null y value into dataset
                    for (let frame_y_index = 1; frame_y_index < frame.length; frame_y_index++) {
                        const y = frame[frame_y_index]
                        if (y === null) continue

                        // add y to dataset that needs sorted
                        y_set.add(frame_y_index);

                        const chart_y_index = frame_y_index - 1

                        // Check if a point with same x already exist
                        const point_index = chart_data.datasets[chart_y_index].data.findIndex(point => (point as Point).x === x);

                        // -1 if not found
                        if (point_index === -1)
                            chart_data.datasets[chart_y_index].data.push({ x, y })
                        else
                            (chart_data.datasets[chart_y_index].data[point_index] as Point).y = y
                    }
                }

                // sort the datasets required
                y_set.forEach(chart_y_index => {
                    (chart_data.datasets[chart_y_index].data as Point[]).sort((a, b) => a.x - b.x)
                })


                break
            }
            case "append": {
                // In append mode, x is assumed to be in ascending order without repeat
                let checked = false
                for (const frame of parseFrames(frames_bytes)) {
                    if (!checked) {
                        // Frame size is assumed to be right, as such only size of the first frame is checked
                        if (frame.length !== y_length + 1) throw Error("Frame size does not match with the config of the chart")

                        checked = true
                    }

                    const x = frame[0] as number

                    // append y value to each dataset
                    for (let frame_y_index = 1; frame_y_index < frame.length; frame_y_index++) {
                        const y = frame[frame_y_index]
                        if (y === null) continue

                        chart_data.datasets[frame_y_index - 1].data.push({ x, y })
                    }
                }
                break
            }

        }
        // update the chart!
        chart.update()
    }

    return onmessage
}

