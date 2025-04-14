import { Chart, type ChartConfiguration, type Point } from "chart.js/auto";

import { qoslabappWs } from "$services/utils";
import type { ChartWebWorkerMessage } from "$states/chart.svelte";
import type { XYChartConfig, XYChartMode } from "qoslab-shared";

// Worker local variables
let _chart: Chart
let _canvas: OffscreenCanvas
let _width: number
let _height: number
let _id: string
let _config: XYChartConfig
let _ws: WebSocket
let _is_drawing_points: boolean

// Message Handlers
function instantiate(id: string, config: XYChartConfig) {
    _id = id
    _config = config
}
function enable_draw_points() {
    _is_drawing_points = true
    if (_chart.options.elements === undefined)
        _chart.options.elements = {}

    if (_chart.options.elements.point === undefined)
        _chart.options.elements.point = {}

    _chart.options.elements.point.radius = 4
    _chart.update()

}

function disable_draw_points() {
    _is_drawing_points = false
    if (_chart.options.elements === undefined)
        _chart.options.elements = {}

    if (_chart.options.elements.point === undefined)
        _chart.options.elements.point = {}

    _chart.options.elements.point.radius = 0
    _chart.update()
}

function set_canvas(canvas: OffscreenCanvas, width?: number, height?: number) {
    _canvas = canvas
    if (width) _canvas.width = width
    if (height) _canvas.height = height


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
                    title: { text: _config!.x_axis, display: true }
                },
                y: {
                    type: "linear",
                    title: { text: _config!.y_axis, display: true }
                }
            },
            elements: {
                point: {
                    radius: 0 // default to disabled in all datasets
                }
            }
        },

    }

    if (_chart !== undefined)
        config.data = _chart.data
    else
        _config.y_names.forEach(y_name => {
            config.data.datasets.push({ data: [], label: y_name })
        })

    _chart = new Chart(_canvas as unknown as HTMLCanvasElement, config)

    if (_ws === undefined || (_ws.readyState !== WebSocket.OPEN && _ws.readyState !== WebSocket.CONNECTING))
        establish_web_socket()
}
function resize(width?: number, height?: number) {
    if (width) {
        _width = width
        _canvas.width = width
    }

    if (height) {
        _height = height
        _canvas.height = height
    }

    _chart.resize(_width, _height - 1)
}
function reset() {
    let new_datasets: { data: Point[], label: string }[] = []
    _config.y_names.forEach(y_name => {
        new_datasets.push({ data: [], label: y_name })
    })
    _chart.data.datasets = new_datasets
    return
}


function establish_web_socket() {
    _ws = new WebSocket(qoslabappWs(`chart/${_id}/${_config.title}`))

    _ws.binaryType = "arraybuffer"

    _ws.onmessage = getWsOnmessageHandler(_config.y_names.length, _config.mode)

    _ws.onclose = (event) => {
        if (event.code !== 4000)
            establish_web_socket()
    }
}






// Webworker onmessage
onmessage = function (event: MessageEvent<ChartWebWorkerMessage>) {
    switch (event.data.type) {
        case "instantiate": {
            const { id, config } = event.data.payload
            instantiate(id, config)
            return
        }
        case "set_canvas": {
            const { canvas, width, height } = event.data.payload
            set_canvas(canvas, width, height)
            return
        }
        case "resize": {
            const { width, height } = event.data.payload
            resize(width, height)
            return
        }
        case "reset": {
            reset()
            return
        }
        case "enable_draw_points": {
            enable_draw_points()
            return
        }
        case "disable_draw_points": {
            disable_draw_points()
            return
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
                        const point_index = _chart.data.datasets[chart_y_index].data.findIndex(point => (point as Point).x === x);

                        // -1 if not found
                        if (point_index === -1)
                            _chart.data.datasets[chart_y_index].data.push({ x, y })
                        else
                            (_chart.data.datasets[chart_y_index].data[point_index] as Point).y = y
                    }
                }

                // sort the datasets required
                y_set.forEach(chart_y_index => {
                    (_chart.data.datasets[chart_y_index].data as Point[]).sort((a, b) => a.x - b.x)
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

                        _chart.data.datasets[frame_y_index - 1].data.push({ x, y })
                    }
                }
                break
            }

        }
        // update the chart!
        _chart.update()
    }

    return onmessage
}

