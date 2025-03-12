import { gstore } from "$states/global.svelte";

import type { AllParamTypes, Experiment } from "qoslab-shared";
import { postRequestJsonInOut, qoslabappUrl } from "./utils";



const headers = {
    "Content-type": "application/json"
}

export async function getAvailableEquipments(): Promise<typeof gstore.workspace.available_equipments> {
    return await postRequestJsonInOut(
        qoslabappUrl("equipment/available_equipments"), {
        prefixes: $state.snapshot(
            Object.values(gstore.workspace.dependencies)
                .filter(d => d.confirmed)
                .map(d => d.name))
    })
}

export async function getAvailableExperiments(): Promise<typeof gstore.workspace.available_equipments> {
    return await postRequestJsonInOut(
        qoslabappUrl("equipment/available_experiments"), {
        prefixes: $state.snapshot(
            Object.values(gstore.workspace.dependencies)
                .filter(d => d.confirmed)
                .map(d => d.name))
    })
}

export async function createEquipment(id: string, module_cls: { module: string, cls: string }) {
    await postRequestJsonInOut(qoslabappUrl("equipment/create_equipment"), { id, ...module_cls })
}

export async function createExperiment(id: string, module_cls: { module: string, cls: string }) {
    await postRequestJsonInOut(qoslabappUrl("equipment/create_experiment"), { id, ...module_cls })
}

export async function getEquipmentParams(id: string): Promise<Record<string, AllParamTypes>> {
    return await postRequestJsonInOut("equipment/get_params", { id })
}

export async function getExperimentParams(id: string): Promise<Record<string, AllParamTypes>> {
    return await postRequestJsonInOut("experiment/get_params", { id })
}

export async function setEquipmentParams(equipment_name: string, params: Record<string, AllParamTypes>) {
    await postRequestJsonInOut("equipment/set_params", { equipment_name, params })
}

export async function setExperimentParams(experiment_name: string, params: Record<string, AllParamTypes>) {
    await postRequestJsonInOut("experiment/set_params", { experiment_name, params })
}

export async function startExperiment(experiments: Experiment[]): Promise<void> {
    await postRequestJsonInOut("experiment/start_experiment_params", {
        experiment: experiments.map(({ name, module, params, cls }) => ({ name, module, params, cls })),
        equipments: $state.snapshot(Object.values(gstore.equipments).map((equipment) => ({
            name: equipment.name,
            module: equipment.module,
            params: equipment.params
        })))
    })
}