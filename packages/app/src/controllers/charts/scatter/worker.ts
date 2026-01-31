import { Chart, type ChartConfiguration, type Point } from "chart.js/auto";
import type { ChartConfig, fromWorkerChartMessages, toWorkerChartMessages } from "../types";
import { cnoc_url, deepCopy } from "$lib/utils";
import { tableFromIPC } from "apache-arrow";


// Worker local variables
let _chart: Chart | undefined = undefined
let _canvas: OffscreenCanvas | undefined = undefined


let _config: ChartConfig | undefined = undefined
let _x_key: string | undefined = undefined

let _ws: WebSocket | undefined = undefined

let _columns: Record<string, number[]> = {}
let _datasets: { data: { x: number, y: number }[], label: string }[] = []


function postErr(message: string) {
    postMessage({ command: "error", payload: { error: message } } satisfies Extract<fromWorkerChartMessages, { command: "error" }>)
}

function post(arg: fromWorkerChartMessages) {
    postMessage(arg)
}


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
        },
        plugins: {
            decimation: {
                enabled: true
            },
        },
    },
} satisfies ChartConfiguration<"line">





type Handler = {
    [K in Pick<toWorkerChartMessages, "command">["command"]]:
    (_: Extract<toWorkerChartMessages, { command: K }>["payload"]) => void
}
const handlers: Handler = {
    set_config: function () { },
    x_key: function () { },
    destroy: function () { },
    ws_open: function () { },
    ws_close: function () { },
    mount: function () { },
    unmount: function () { },
    resize: function () { },
    set_is_drawing_points: function () { },
    zoom: function () { },
    pan: function () { },
    auto_axis: function () { },
    enable_tooltip: function () { },
    disable_tooltip: function () { },
}

handlers.set_config = function set_config({ config }) {
    _config = config
    _chart_config.data.datasets = config.columns.map(label => ({ data: [], label }))
    _columns = {}
    for (const column of config.columns) {
        _columns[column] = []
    }
    _datasets = config.columns.map(label => ({ data: [], label }))

    // _chart_config.options.scales.x.title.text = _scatter_config.x_axis
    // _chart_config.options.scales.y.title.text = _scatter_config.y_axis
}

handlers.x_key = function x_key({ x_key }) {
    _x_key = x_key
}

handlers.destroy = function clear() {
    if (_chart === undefined) return
    _chart.destroy()
    _canvas = undefined
}

handlers.ws_open = function ws_open() {
    if (_ws !== undefined && (_ws.readyState === WebSocket.OPEN || _ws.readyState === WebSocket.CONNECTING))
        postErr("Scatter worker: WebSocket is already connected")

    _ws = new WebSocket(cnoc_url + "chart/" + _config!.title)
    _ws.binaryType = "arraybuffer"

    _ws.onclose = (event) => {
        post({ command: "ws_closed" })
    }

    _ws.onmessage = (event: MessageEvent<ArrayBuffer>) => {

        const table = tableFromIPC(event.data)



        const x_column = table.getChild(_x_key!)!

        for (const column of table.schema.fields) {
            for (let i = 0; i < table.getChild(column.name)!.length; i++) {
                // Update the columns
                _columns[column.name].push(Number(table.getChild(column.name)!.get(i)!))

                // Update the datasets
                if (column.name === _x_key) continue
                const dataset = _datasets.find(dataset => dataset.label === column.name)!
                dataset.data.push({ x: Number(x_column.get(i)!), y: Number(table.getChild(column.name)!.get(i)!) })
            }

        }

        decimate_datasets_and_update_chart()
    }
}

handlers.ws_close = function ws_close() {
    if (_ws === undefined) return
    _datasets = []
    _columns = {}
    _ws.close()
}

handlers.mount = function mount({ canvas, width, height }) {
    // Make sure its in fresh state
    _canvas = canvas
    _canvas.width = width
    _canvas.height = height

    if (_chart !== undefined) {
        postErr("Scatter worker: Chart shall not exist when mount is called")
        return
    }

    _chart = new Chart(_canvas as unknown as HTMLCanvasElement, deepCopy(_chart_config))
    decimate_datasets_and_update_chart()
    _chart!.update()
}

handlers.unmount = function unmount() {
    if (_chart === undefined) {
        postErr("Scatter worker: Chart shall exist when unmount is called")
        return
    }

    _chart.destroy()
    _chart = undefined
    _canvas = undefined
}

handlers.set_is_drawing_points = function set_is_drawing_points({ is_drawing_points }) {
    if (_chart) {
        _chart.options.elements!.point!.radius = is_drawing_points ? 4 : 0
        _chart.update()
    }
    _chart_config.options.elements.point.radius = is_drawing_points ? 4 : 0
}

handlers.resize = function resize({ width, height }) {
    if (_canvas === undefined || _chart === undefined) return

    _canvas.width = width
    _canvas.height = height
    _chart.resize(width, height)
    decimate_datasets_and_update_chart()
}

handlers.zoom = function zoom({ direction, x, y }) {
    if (_chart === undefined) return


    const factor = direction === "in" ? 0.9 : 1.1

    // Determine where the zoom position is along x axis
    if (x) {
        const x_value = _chart.scales.x.getValueForPixel(x)
        if (x_value === undefined) { return }

        const old_x_min = _chart.scales.x.min
        const old_x_max = _chart.scales.x.max

        const new_x_min = x_value - factor * (x_value - old_x_min)
        const new_x_max = x_value + factor * (old_x_max - x_value)

        _chart.options!.scales!.x!.min = new_x_min
        _chart.options!.scales!.x!.max = new_x_max

    }

    // Determine where the zoom position is along y axis
    if (y) {
        const y_value = _chart.scales.y.getValueForPixel(y)
        if (y_value === undefined) { return }

        const old_y_min = _chart.scales.y.min
        const old_y_max = _chart.scales.y.max

        const new_y_min = y_value - factor * (y_value - old_y_min)
        const new_y_max = y_value + factor * (old_y_max - y_value)

        _chart.options!.scales!.y!.min = new_y_min
        _chart.options!.scales!.y!.max = new_y_max
    }

    decimate_datasets_and_update_chart()
}


handlers.pan = function pan({ old_x, old_y, new_x, new_y }) {
    if (_chart === undefined) return

    const old_x_value = _chart.scales.x.getValueForPixel(old_x)
    if (old_x_value === undefined) return

    const old_y_value = _chart.scales.y.getValueForPixel(old_y)
    if (old_y_value === undefined) return

    const new_x_value = _chart.scales.x.getValueForPixel(new_x)
    if (new_x_value === undefined) return

    const new_y_value = _chart.scales.y.getValueForPixel(new_y)
    if (new_y_value === undefined) return

    const x_offset = new_x_value - old_x_value
    const y_offset = new_y_value - old_y_value

    _chart.options!.scales!.x!.min = _chart.scales.x.min - x_offset
    _chart.options!.scales!.x!.max = _chart.scales.x.max - x_offset
    _chart.options!.scales!.y!.min = _chart.scales.y.min - y_offset
    _chart.options!.scales!.y!.max = _chart.scales.y.max - y_offset

    decimate_datasets_and_update_chart()
}

handlers.auto_axis = function auto_axis() {
    if (_chart === undefined) return

    _chart.options!.scales!.x!.min = undefined
    _chart.options!.scales!.x!.max = undefined
    _chart.options!.scales!.y!.min = undefined
    _chart.options!.scales!.y!.max = undefined

    decimate_datasets_and_update_chart()
}

handlers.enable_tooltip = function enable_tooltip({ x, y }) {
    if (_chart === undefined) return

    // Reset tooltip
    const tooltip = _chart.tooltip!;
    if (tooltip.getActiveElements().length > 0)
        tooltip.setActiveElements([], { x: 0, y: 0 });

    // Get the x y values
    const x_value = _chart.scales.x.getValueForPixel(x)
    const y_value = _chart.scales.y.getValueForPixel(y)
    if (x_value === undefined || y_value === undefined) return

    // Find the nearest datapoint
    let datasetIndex = 0
    let index = 0
    let distance = Math.abs((_chart.data.datasets[0].data[0]! as Point).x! - x_value) + Math.abs((_chart.data.datasets[0].data[0]! as Point).y! - y_value)
    _chart.data.datasets.forEach((dataset, di) => {
        (dataset.data as Point[]).forEach(({ x: data_x, y: data_y }, i) => {
            const distance_x = Math.abs(x_value - data_x!)
            const distance_y = Math.abs(y_value - data_y!)
            if (distance_x + distance_y < distance) {
                distance = distance_x + distance_y
                datasetIndex = di
                index = i
            }
        })
    })

    // Find the nearest point
    const chartArea = _chart.chartArea;

    tooltip.setActiveElements([{ datasetIndex, index }],
        {
            x: (chartArea.left + chartArea.right) / 2,
            y: (chartArea.top + chartArea.bottom) / 2,
        });

    _chart.update();
}

handlers.disable_tooltip = function disable_tooltip() {
    if (_chart === undefined) return

    // Reset tooltip
    _chart.tooltip!.setActiveElements([], { x: 0, y: 0 });

    _chart.update();
}


// Webworker onmessage
onmessage = function (event: MessageEvent<toWorkerChartMessages>) {

    handlers[event.data.command](event.data.payload as Extract<toWorkerChartMessages, [typeof event.data.command]>)

}

function decimate_datasets_and_update_chart() {
    // Determine if the chart should be decimated
    if (_chart === undefined || _canvas === undefined) return

    const axis_x_min = _chart.scales.x.min
    const axis_x_max = _chart.scales.x.max

    const chart_datasets = []



    // Determine the range of x index
    let x_min_index = 0
    let x_max_index = _columns[_x_key!].length - 1

    if (_chart.options!.scales!.x!.min !== undefined) {
        let x_min_found = false
        let x_max_found = false
        x_min_index = -1
        for (let i = 0; i < _columns[_x_key!].length; i++) {
            const x = _columns[_x_key!][i]
            if (x >= axis_x_min && !x_min_found) {
                x_min_index = i;
                if (x_min_index > 0) x_min_index -= 1
                x_min_found = true
            }
            if (x >= axis_x_max && !x_max_found) { x_max_index = i - 1; x_max_found = true }
            if (x_min_found && x_max_found) break
        }

        // Skip rendering if the x range is out of bounds
        if (x_min_index === -1) return
    }
    const ratio = Math.floor((x_max_index - x_min_index) / _canvas.width)

    // Construct the chart datasets
    for (const column of _config!.columns) {
        if (column === _x_key) continue
        const data: { x: number, y: number }[] = []
        for (let i = x_min_index; i <= x_max_index; i++) {
            data.push({ x: _columns[_x_key!][i], y: _columns[column][i] })
        }

        if (ratio < 4) {
            chart_datasets.push({ data, label: column })
            continue
        }

        chart_datasets.push({ data: decimate(data, ratio), label: column })
    }

    postErr({ data: chart_datasets, x_min_index, x_max_index })

    _chart.data.datasets = chart_datasets
    _chart.update()
}

function decimate(data: { x: number, y: number }[], decimation: number) {
    const res: { x: number, y: number }[] = []

    for (let i = 0; i < data.length; i += decimation) {
        if (i + decimation > data.length) break

        const decimation_range = data.slice(i, i + decimation)
        const min = Math.min(...decimation_range.map(v => v.y))
        const max = Math.max(...decimation_range.map(v => v.y))

        if (decimation % 2 === 1) {
            res.push({ x: data[i + (decimation - 1) / 2].x, y: min })
            res.push({ x: data[i + (decimation - 1) / 2].x, y: max })
            continue
        }

        const x = (
            data[Math.floor(i + decimation / 2)].x +
            data[Math.ceil(i + decimation / 2)].x
        ) / 2

        res.push({ x, y: min })
        res.push({ x, y: max })
    }

    return res
}