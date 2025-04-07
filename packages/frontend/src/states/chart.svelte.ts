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
    config: T
    worker: Worker | undefined
    constructor(config: T) {
        this.config = config
    }
    reset() {
        if (this.worker) this.worker.postMessage({ type: "reset" })
    }

}

export class Charts {
    charts: Record<string, Chart> = $state({})


    instantiate(config: ChartConfigs) {
        if (this.charts[config.title] === undefined)
            this.charts[config.title] = new Chart(config)
        else
            this.charts[config.title].reset()
    }



}
