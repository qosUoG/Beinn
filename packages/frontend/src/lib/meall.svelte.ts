import type { EEType } from "$states/ee.svelte";
import { type Availables } from "$states/global.svelte";
import type { AllParamTypes } from "$states/params.svelte";
import { retryOnError } from "$states/utils.svelte";
import { message } from "@tauri-apps/plugin-dialog";

import { postRequestJsonInOut } from "./utils";

export const meallUrl = (path: string) => `http://localhost:8000/${path}`

export const meallWs = (path: string) => `ws://localhost:8000/${path}`

export async function meallGetAvailableEEs(eetype: EEType, payload: { prefixes: string[] }): Promise<Availables> {
    return await postRequestJsonInOut(meallUrl(`${eetype}/available_${eetype}s`), payload)
}

export async function meallCreateEE(eetype: EEType, payload: { id: string, module_cls: { module: string, cls: string } }) {
    await postRequestJsonInOut(meallUrl(`${eetype}/create`), { id: payload.id, ...payload.module_cls })
}

export async function meallGetEEParams(eetype: EEType, payload: { id: string }): Promise<Record<string, AllParamTypes>> {
    return await postRequestJsonInOut(meallUrl(`${eetype}/get_params`), payload)
}

export async function meallSetEEParams(eetype: EEType, payload: { id: string, params: Record<string, AllParamTypes> }) {
    await postRequestJsonInOut(meallUrl(`${eetype}/set_params`), payload)
}

export async function meallRemoveEE(eetype: EEType, payload: { id: string }) {
    await postRequestJsonInOut(meallUrl(`${eetype}/remove`), payload)
}

export async function meallStartExperiment(payload: { id: string }) {
    await postRequestJsonInOut(meallUrl("experiment/start"), payload)
}

export async function meallPauseExperiment(payload: { id: string }) {
    await postRequestJsonInOut(meallUrl("experiment/pause"), payload)
}

export async function meallContinueExperiment(payload: { id: string }) {
    await postRequestJsonInOut(meallUrl("experiment/continue"), payload)
}

export async function meallStopExperiment(payload: { id: string }) {
    await postRequestJsonInOut(meallUrl("experiment/stop"), payload)
}

export async function meallGetPid(): Promise<{ pid: number }> {
    return await postRequestJsonInOut(meallUrl("workspace/pid"), {})
}

export function meallGetExperimentEventsWs<T extends any>(payload: { id: string, onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    let socket = new WebSocket(meallWs(`experiment/${payload.id}/events`))
    socket.onmessage = payload.onmessage
    socket.onclose = () => {
        socket = new WebSocket(meallWs(`experiment/${payload.id}/events`))
    }
    return socket

}

export function meallGetChartDataWs<T extends any>(payload: { id: string, title: string, onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    const socket = new WebSocket(meallWs(`chart/${payload.id}/events`))
    socket.onmessage = payload.onmessage
    return socket
}

export function meallGetCliWs<T extends any>(payload: { onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    const socket = new WebSocket(meallWs(`cli`))
    socket.onmessage = payload.onmessage
    return socket
}

export async function meallWaitUntilOnline(timeout: number = 5000) {
    await retryOnError(5000, async () => {
        const res = await (await fetch(meallUrl("workspace/status"))).json();
        if (res.status !== "online")
            throw Error()
    });

    const res = await (await fetch(meallUrl("workspace/status"))).json();
    if (res.status !== "online")
        await message("Timeout trying to start meall. meall is not online", { title: "meall startup timeout", "kind": "error" })
}