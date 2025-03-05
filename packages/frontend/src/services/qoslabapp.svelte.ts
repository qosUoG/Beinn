import { gstore } from "$states/global.svelte";

import type { AllParamTypes } from "qoslab-shared";



const headers = {
    "Content-type": "application/json"
}

export async function getAvailableEquipments() {
    return await (await fetch(`http://localhost:8000/workspace/available_equipments`, {
        method: "POST",
        body: JSON.stringify({
            names: $state.snapshot(Object.values(gstore.workspace.dependencies).filter(d => d.confirmed).map(d => d.name))
        }),

        headers
    })).json() as {
        module: string;
        cls: string;
    }[]
}

export async function getEquipmentParams(path: { module: string, cls: string }): Promise<Record<string, AllParamTypes>> {
    return await (
        await fetch(
            `http://localhost:8000/equipment/get_params`,
            {
                method: "POST",
                body: JSON.stringify(path),
                headers
            }
        )
    ).json()
}



export async function startExperiments(): Promise<void> {


    await fetch(
        "http://localhost:8000/workspace/start_experiments",
        {
            method: "POST",
            body: JSON.stringify(
                {
                    experiments: $state.snapshot(Object.values(gstore.experiments).map((experiment) => ({
                        name: experiment.name,
                        module: experiment.module,
                        params: experiment.params
                    }))),
                    equipments: $state.snapshot(Object.values(gstore.equipments).map((equipment) => ({
                        name: equipment.name,
                        module: equipment.module,
                        params: equipment.params
                    })))
                }
            ),
            headers
        }
    )

}