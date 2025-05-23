import type { Availables, EEType } from "$states/ee.svelte";

import type { AllParamTypes } from "$states/params.svelte";

import { message } from "@tauri-apps/plugin-dialog";

import { getRequestJsonOut_throwable, postRequestJsonInOut_throwable, retryOnError } from "./utils";
import { meallUrl, meallWs } from "./meall";



export async function meallGetAvailableEEs_throwable(eetype: EEType, payload: { prefixes: string[] }): Promise<Availables> {
    return await postRequestJsonInOut_throwable(meallUrl(`${eetype}/available_${eetype}s`), payload)
}

export async function meallCreateEE_throwable(eetype: EEType, payload: { id: string, module_cls: { module: string, cls: string } }) {
    await postRequestJsonInOut_throwable(meallUrl(`${eetype}/create`), { id: payload.id, ...payload.module_cls })
}

export async function meallGetEEParams_throwable(eetype: EEType, payload: { id: string }): Promise<Record<string, AllParamTypes>> {
    return await postRequestJsonInOut_throwable(meallUrl(`${eetype}/get_params`), payload)
}

export async function meallSetEEParams_throwable(eetype: EEType, payload: { id: string, params: Record<string, AllParamTypes> }) {
    await postRequestJsonInOut_throwable(meallUrl(`${eetype}/set_params`), payload)
}

export async function meallRemoveEE_throwable(eetype: EEType, payload: { id: string }) {
    await postRequestJsonInOut_throwable(meallUrl(`${eetype}/remove`), payload)
}

export async function meallStartExperiment_throwable(payload: { id: string }) {
    await postRequestJsonInOut_throwable(meallUrl("experiment/start"), payload)
}

export async function meallPauseExperiment_throwable(payload: { id: string }) {
    await postRequestJsonInOut_throwable(meallUrl("experiment/pause"), payload)
}

export async function meallContinueExperiment_throwable(payload: { id: string }) {
    await postRequestJsonInOut_throwable(meallUrl("experiment/continue"), payload)
}

export async function meallStopExperiment_throwable(payload: { id: string }) {
    await postRequestJsonInOut_throwable(meallUrl("experiment/stop"), payload)
}

export async function meallGetPid_throwable(): Promise<number> {
    return await getRequestJsonOut_throwable(meallUrl("workspace/pid"));

}

export async function meallKill_throwable(): Promise<void> {
    await getRequestJsonOut_throwable(meallUrl("workspace/kill"));

}

export function meallGetExperimentEventsWs<T extends any>(payload: { id: string, onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    let socket = new WebSocket(meallWs(`experiment/${payload.id}/events`))
    socket.onmessage = payload.onmessage
    socket.onclose = () => {
        socket = new WebSocket(meallWs(`experiment/${payload.id}/events`))
    }
    return socket

}


export function meallGetCliWs<T extends any>(payload: { onmessage: (this: WebSocket, event: MessageEvent<T>) => any }) {
    const socket = new WebSocket(meallWs(`cli`))
    socket.onmessage = payload.onmessage
    return socket
}

export async function meallWaitUntilOnline(timeout: number = 5000) {
    let success = false
    await retryOnError(timeout, async () => {
        await getRequestJsonOut_throwable(meallUrl("workspace/online"));
        success = true
    });

    if (!success)
        await message("Timeout trying to start meall. meall is not online", { title: "meall startup timeout", "kind": "error" })
}