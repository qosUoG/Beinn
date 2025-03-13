import { gstore } from "$states/global.svelte";
import type { AllParamTypes, Experiment } from "qoslab-shared";
import { postRequestJsonInOut, qoslabappUrl } from "./utils";

type EEType = "equipment" | "experiment"

async function getAvailableEEs(eetype: EEType): Promise<typeof gstore.workspace.available_equipments> {
    return await postRequestJsonInOut(
        qoslabappUrl(`${eetype}/available_${eetype}s`), {
        prefixes: $state.snapshot(
            Object.values(gstore.workspace.dependencies)
                .filter(d => d.confirmed)
                .map(d => d.name))
    })
}

export const getAvailableEquipments = async () => await getAvailableEEs("equipment")
export const getAvailableExperiments = async () => await getAvailableEEs("experiment")


type OmitFirstParamType<T extends (...args: any) => any> = T extends (
    ignored: infer _,
    ...args: infer P
) => any ? P : never

async function createEE(eetype: EEType, payload: { id: string, module_cls: { module: string, cls: string } }) {
    await postRequestJsonInOut(qoslabappUrl(`${eetype}/create`), { id: payload.id, ...payload.module_cls })
}

export const createEquipment = async (...args: OmitFirstParamType<typeof createEE>) => await createEE("equipment", ...args)

export const createExperiment = async (...args: OmitFirstParamType<typeof createEE>) => await createEE("experiment", ...args)


async function getEEParams(eetype: EEType, payload: { id: string }): Promise<Record<string, AllParamTypes>> {
    return await postRequestJsonInOut(qoslabappUrl(`${eetype}/get_params`), payload)
}

export const getEquipmentParams = async (...args: OmitFirstParamType<typeof getEEParams>) => await getEEParams("equipment", ...args)

export const getExperimentParams = async (...args: OmitFirstParamType<typeof getEEParams>) => await getEEParams("experiment", ...args)


async function setEEParams(eetype: EEType, payload: { id: string, params: Record<string, AllParamTypes> }) {
    await postRequestJsonInOut(qoslabappUrl(`${eetype}/set_params`), payload)
}

export const setEquipmentParams = async (...args: OmitFirstParamType<typeof setEEParams>) => await setEEParams("equipment", ...args)

export const setExperimentParams = async (...args: OmitFirstParamType<typeof setEEParams>) => await setEEParams("experiment", ...args)


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