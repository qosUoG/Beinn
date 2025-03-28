import { gstore } from "$states/global.svelte";
import type { AllParamTypes, CreatedExperiment, EEType } from "qoslab-shared";
import { postRequestJsonInOut, qoslabappUrl, qoslabappWs } from "./utils";



export async function getAvailableEEs(eetype: EEType): Promise<typeof gstore.workspace.available_equipments> {
    const res = await postRequestJsonInOut(
        qoslabappUrl(`${eetype}/available_${eetype}s`), {
        prefixes: $state.snapshot(
            Object.values(gstore.workspace.dependencies)
                .filter(d => d.confirmed)
                .map(d => d.name))
    })
    console.log(res)
    return res
}

export async function createEE(eetype: EEType, payload: { id: string, module_cls: { module: string, cls: string } }) {
    await postRequestJsonInOut(qoslabappUrl(`${eetype}/create`), { id: payload.id, ...payload.module_cls })
}

export async function getEEParams(eetype: EEType, payload: { id: string }): Promise<Record<string, AllParamTypes>> {
    return await postRequestJsonInOut(qoslabappUrl(`${eetype}/get_params`), payload)
}

export async function setEEParams(eetype: EEType, payload: { id: string, params: Record<string, AllParamTypes> }) {
    await postRequestJsonInOut(qoslabappUrl(`${eetype}/set_params`), payload)
}

export async function removeEE(eetype: EEType, payload: { id: string }) {
    await postRequestJsonInOut(qoslabappUrl(`${eetype}/remove`), payload)
}

export async function startExperiment(payload: { id: string }): Promise<void> {
    await postRequestJsonInOut(qoslabappUrl("experiment/start"), payload)
}

export async function pauseExperiment(payload: { id: string }): Promise<void> {
    await postRequestJsonInOut(qoslabappUrl("experiment/pause"), payload)
}

export async function continueExperiment(payload: { id: string }): Promise<void> {
    await postRequestJsonInOut(qoslabappUrl("experiment/continue"), payload)
}

export async function stopExperiment(payload: { id: string }): Promise<void> {
    await postRequestJsonInOut(qoslabappUrl("experiment/stop"), payload)
}

export function subscribeExperimentEventsWs<T extends any>(payload: { id: string, onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    const socket = new WebSocket(qoslabappWs(`experiment/${payload.id}/events`))
    socket.onmessage = payload.onmessage

}

export function subscribeChartDataWs<T extends any>(payload: { id: string, title: string, onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    const socket = new WebSocket(qoslabappWs(`chart/${payload.id}/events`))
    socket.onmessage = payload.onmessage
}

export function connnectCliWs<T extends any>(payload: { onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    const socket = new WebSocket(qoslabappWs(`cli`))
    socket.onmessage = payload.onmessage
    return socket
}