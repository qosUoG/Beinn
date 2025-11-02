import { Chart, type ChartConfiguration, type ChartData, type Point } from "chart.js/auto";
import type { ScatterConfig } from "./scatter";
import type { ChartMessages } from "../types";
import { cnoc_url, deepCopy } from "$lib/utils";


// Worker local variables
let _chart: Chart | undefined = undefined
let _canvas: OffscreenCanvas | undefined = undefined


let _scatter_config: ScatterConfig
let _ws: WebSocket

let _datasets: { data: { x: number, y: number }[], label: string }[] = []
let _ws_interval: Timer | undefined




const _chart_config = {
    type: "line",
    data: {
        datasets: [{ data: [], label: "" }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        resizeDelay: 500,
        animation: false,
        parsing: false,

        scales: {
            x: {
                type: "linear",
                title: { text: "", display: true }
            },
            y: {
                type: "linear",
                title: { text: "", display: true }
            }
        },
        elements: {
            point: {
                radius: 0
            },
            line: {
                borderWidth: 2
            }
        }
    },

} satisfies ChartConfiguration<"line">




type Handler = {
    [K in Pick<ChartMessages, "command">["command"]]:
    (_: Extract<ChartMessages, { command: K }>["payload"]) => void
}
const handlers: Handler = {
    instantiate: function () { },
    set_canvas: function () { },
    resize: function () { },
    set_is_drawing_points: function () { },
    destroy: function () { },
    hide: function () { },
    show: function () { },
    restart: function () { }
}





handlers.instantiate = function instantiate({ config }: { config: ScatterConfig }) {
    _scatter_config = config

    resetConfig()
}

handlers.set_is_drawing_points = function set_is_drawing_points({ is_drawing_points }: { is_drawing_points: boolean }) {
    if (_chart) {
        _chart.options.elements!.point!.radius = is_drawing_points ? 4 : 0
        _chart.update()
    }
    _chart_config.options.elements.point.radius = is_drawing_points ? 4 : 0
}

handlers.resize = function resize({ width, height }: { width: number, height: number }) {
    if (_canvas && _chart) {
        _canvas.width = width
        _canvas.height = height
        _chart.resize(width, height)
        _chart.update()


    }
}

handlers.set_canvas = function set_canvas({ canvas, width, height }: { canvas: OffscreenCanvas, width: number, height: number }) {

    _canvas = canvas
    _canvas.width = width
    _canvas.height = height

    if (_chart !== undefined)
        _chart.destroy()

    _chart = new Chart(_canvas as unknown as HTMLCanvasElement, deepCopy(_chart_config))

    // load previous chart data 
    updateData()


    // Establish websocket connection if not already established
    wsConnect()
}

handlers.show = function show() {

    if (_ws !== undefined)
        _ws.close(4000)

    if (_ws_interval !== undefined) {
        clearInterval(_ws_interval)
        _ws_interval = undefined
    }

    resetConfig()
    _decimation = 0

    if (_chart) _chart.destroy()

    if (_canvas)
        _chart = new Chart(_canvas as unknown as HTMLCanvasElement, deepCopy(_chart_config))

    // load previous chart data 
    updateData()


    // Establish websocket connection if not already established
    wsConnect()

}


handlers.hide = function hide() {
    if (_chart) _chart.destroy()
    _canvas = undefined

    _online = false


    if (_ws !== undefined) {
        _ws.onclose = null
        _ws.close(4000)
    }

    if (_ws_interval !== undefined) {
        clearInterval(_ws_interval)
        _ws_interval = undefined
    }
}

handlers.destroy = function destroy() {
    _canvas = undefined
    if (_chart) {
        _chart.destroy()
        _chart = undefined
    }
}

handlers.restart = function restart() {
    resetConfig()
    wsConnect()
}

function resetConfig() {
    _chart_config.data.datasets = _scatter_config.y_names.map(label => ({ data: [], label }))
    _chart_config.options.scales.x.title.text = _scatter_config.x_axis
    _chart_config.options.scales.y.title.text = _scatter_config.y_axis
    _datasets = _scatter_config.y_names.map(label => ({ data: [], label }))
}



let _online = false
let _pending_update = false
let _update_timeout: Timer | undefined = undefined
function wsConnect() {


    const wsNotConnected = () =>
        (_ws === undefined || (_ws.readyState !== WebSocket.OPEN && _ws.readyState !== WebSocket.CONNECTING))

    if (!wsNotConnected()) return


    _ws = new WebSocket(cnoc_url + "chart/" + _scatter_config.title)
    _ws.binaryType = "arraybuffer"

    _ws.onopen = () => {
        _online = true
        // Run once every 10 seconds so it does not fall asleep
        _ws_interval = setInterval(() => {
            if (_online && wsNotConnected()) wsConnect()
        }, 10000)
    }

    _ws.onclose = (event) => {
        if (event.code !== 4000) {

            wsConnect()
            postMessage("ws closed")
            postMessage(event.code)
        }
        else
            _online = false
    }


    _ws.onmessage = (event: MessageEvent<ArrayBuffer>) => {
        const y_length = _chart_config.data.datasets.length

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




        switch (_scatter_config.mode) {
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
                        const point_index = _datasets[chart_y_index].data.findIndex(point => (point as Point).x === x);

                        // -1 if not found
                        if (point_index === -1)
                            _datasets[chart_y_index].data.push({ x, y })
                        else
                            (_datasets[chart_y_index].data[point_index] as Point).y = y
                    }
                }

                // sort the datasets required
                y_set.forEach(chart_y_index => {
                    (_datasets[chart_y_index].data as Point[]).sort((a, b) => a.x! - b.x!)
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

                        _datasets[frame_y_index - 1].data.push({ x, y })
                    }
                }
                break
            }

        }

        // Flag that update is pending
        if (_update_timeout !== undefined) {
            _pending_update = true
            return
        }

        updateData()

        _update_timeout = setInterval(() => {
            if (_pending_update) {
                updateData()
                return
            }
            clearInterval(_update_timeout)
            _update_timeout = undefined
        }, 200)




    }


}




let _decimation = 0

function updateData() {

    if (_chart === undefined || _canvas === undefined) return

    const width = _canvas.width
    const data_length = _datasets[0].data.length
    const number_of_datasets = _datasets.length
    // Decimate data only if needed
    if (data_length < width * 4) {
        _chart.data.datasets = _datasets
        _chart.update()

        return
    }

    const new_decimation = Math.floor(data_length / width)

    // Cursor to start decimating from
    let from_index = 0

    if (new_decimation === _decimation) {
        // If decimation still the same, check if new data points is enough to form new decimation
        const old_data_length = _chart.data.datasets[0].data.length

        // Not enough data
        if (data_length < old_data_length + _decimation)
            return

        // Cursor for decimating new point(s)
        from_index = old_data_length * _decimation / 2


    } else {
        // Otherwise, start from scratch
        _decimation = new_decimation

        _chart.destroy()
        _chart = new Chart(_canvas as unknown as HTMLCanvasElement, deepCopy(_chart_config))
    }

    for (let i = from_index; i < data_length; i += _decimation) {

        // First check if reached end of possible decimation
        if (i + _decimation >= data_length)
            break

        // Decimate each dataset
        for (let d_i = 0; d_i < number_of_datasets; d_i++) {
            const slice = _datasets[d_i].data.slice(i + 1, i + _decimation)

            let min_y = _datasets[d_i].data[i].y
            let max_y = _datasets[d_i].data[i].y

            for (let s_i = 0; s_i < slice.length; s_i++) {
                if (slice[s_i].y < min_y) min_y = slice[s_i].y
                else if (slice[s_i].y > max_y) max_y = slice[s_i].y
            }

            const min_x = _datasets[d_i].data[i].x
            const max_x = min_x + (slice[slice.length - 1].x - _datasets[d_i].data[i].x) / 2

            _chart.data.datasets[d_i].data.push({ x: min_x, y: min_y })

            _chart.data.datasets[d_i].data.push({ x: max_x, y: max_y })

        }
    }
    _chart.update()
    _pending_update = false


}













// Webworker onmessage
onmessage = function (event: MessageEvent<ChartMessages>) {

    handlers[event.data.command](event.data.payload as Extract<ChartMessages, [typeof event.data.command]>)
    //     case "kill": {
    //         _online = false

    //         _chart.destroy()
    //         if (_ws !== undefined) {
    //             _ws.onclose = null
    //             _ws.close(4000)
    //         }

    //         if (_ws_interval !== undefined)
    //             clearInterval(_ws_interval)
    //     }
    // }
}

