import { gstore, type Availables } from "$states/global.svelte";
import type { AllParamTypes, EEType } from "qoslab-shared";
import { postRequestJsonInOut, qoslabappUrl, qoslabappWs } from "./utils";



export async function qoslabappGetAvailableEEs(eetype: EEType, payload: { prefixes: string[] }): Promise<Availables> {
    return await postRequestJsonInOut(qoslabappUrl(`${eetype}/available_${eetype}s`), payload)
}

export async function qoslabappCreateEE(eetype: EEType, payload: { id: string, module_cls: { module: string, cls: string } }): Promise<Record<string, AllParamTypes>> {
    return await postRequestJsonInOut(qoslabappUrl(`${eetype}/create`), { id: payload.id, ...payload.module_cls })
}

export async function qoslabappGetEEParams(eetype: EEType, payload: { id: string }): Promise<Record<string, AllParamTypes>> {
    return await postRequestJsonInOut(qoslabappUrl(`${eetype}/get_params`), payload)
}

export async function qoslabappSetEEParams(eetype: EEType, payload: { id: string, params: Record<string, AllParamTypes> }) {
    await postRequestJsonInOut(qoslabappUrl(`${eetype}/set_params`), payload)
}

export async function qoslabappRemoveEE(eetype: EEType, payload: { id: string }) {
    await postRequestJsonInOut(qoslabappUrl(`${eetype}/remove`), payload)
}

export async function qoslabappStartExperiment(payload: { id: string }) {
    await postRequestJsonInOut(qoslabappUrl("experiment/start"), payload)
}

export async function qoslabappPauseExperiment(payload: { id: string }) {
    await postRequestJsonInOut(qoslabappUrl("experiment/pause"), payload)
}

export async function qoslabappContinueExperiment(payload: { id: string }) {
    await postRequestJsonInOut(qoslabappUrl("experiment/continue"), payload)
}

export async function qoslabappStopExperiment(payload: { id: string }) {
    await postRequestJsonInOut(qoslabappUrl("experiment/stop"), payload)
}

export function qoslabappGetExperimentEventsWs<T extends any>(payload: { id: string, onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    const socket = new WebSocket(qoslabappWs(`experiment/${payload.id}/events`))
    socket.onmessage = payload.onmessage
    return socket

}

export function qoslabappGetChartDataWs<T extends any>(payload: { id: string, title: string, onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    const socket = new WebSocket(qoslabappWs(`chart/${payload.id}/events`))
    socket.onmessage = payload.onmessage
    return socket
}

export function qoslabappGetCliWs<T extends any>(payload: { onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    const socket = new WebSocket(qoslabappWs(`cli`))
    socket.onmessage = payload.onmessage
    return socket
}