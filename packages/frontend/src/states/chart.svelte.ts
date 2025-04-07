import type { ChartConfigs, XYChartConfig } from "qoslab-shared"




export type XYWebWorkerMessage = {
    type: "instantiate",
    payload: {
        canvas: OffscreenCanvas,
        id: string,
        config: XYChartConfig
        width: number,
        height: number
    }
} | {
    type: "resize",
    payload: { width: number, height: number }
} | {
    type: "reset"
}



export class Chart<T = ChartConfigs> {
    accessor config: T
    worker: Worker | undefined
    constructor(config: T) {
        this.config = config
    }
    reset() {
        if (this.worker) this.worker.postMessage({ type: "reset" })
    }

}

export class Charts {
    private _charts: Record<string, Chart> = $state({})
    get charts() {
        return this._charts
    }

    instantiate(config: ChartConfigs) {
        if (this._charts[config.title] === undefined)
            this._charts[config.title] = new Chart(config)
        else
            this._charts[config.title].reset()
    }



}
