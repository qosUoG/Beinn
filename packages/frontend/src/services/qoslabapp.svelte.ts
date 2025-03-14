import { gstore } from "$states/global.svelte";
import type { AllParamTypes, ChartConfigs, EEType } from "qoslab-shared";
import { postRequestJsonInOut, qoslabappUrl } from "./utils";



export async function getAvailableEEs(eetype: EEType): Promise<typeof gstore.workspace.available_equipments> {
    return await postRequestJsonInOut(
        qoslabappUrl(`${eetype}/available_${eetype}s`), {
        prefixes: $state.snapshot(
            Object.values(gstore.workspace.dependencies)
                .filter(d => d.confirmed)
                .map(d => d.name))
    })
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

export async function getChartConfigsByExperimentId(payload: { id: string }): Promise<{ charts: Record<string, ChartConfigs> }> {
    return await postRequestJsonInOut(qoslabappUrl(`chart/configs`), payload)
}


// export async function startExperiment(experiments: Experiment[]): Promise<void> {
//     await postRequestJsonInOut("experiment/start_experiment_params", {
//         experiment: experiments.map(({ name, module, params, cls }) => ({ name, module, params, cls })),
//         equipments: $state.snapshot(Object.values(gstore.equipments).map((equipment) => ({
//             name: equipment.name,
//             module: equipment.module,
//             params: equipment.params
//         })))
//     })
// }