import { gstore } from "$states/global.svelte";
import type { Directory } from "$states/types/general";
import type { AllParamTypes } from "$states/types/params";


export async function setWorkspaceDirectory(path: string): Promise<string[]> {
    return await (
        await fetch(
            `http://localhost:8000/workspace/set_directory`,
            {
                method: "POST",
                body: JSON.stringify({ path }),
                headers: {
                    "Content-type": "application/json"
                },
            }
        )
    ).json();
}

export async function getEquipmentParams(path: string): Promise<Record<string, AllParamTypes>> {
    return await (
        await fetch(
            `http://localhost:8000/equipment/get_params/${encodeURIComponent(path)}`
        )
    ).json()
}



export async function startExperiments(): Promise<void> {
    console.log((
        {
            experiments: $state.snapshot(Object.values(gstore.experiments).map((experiment) => ({
                name: experiment.name,
                path: experiment.path,
                params: experiment.params
            }))),
            equipments: $state.snapshot(Object.values(gstore.equipments).map((equipment) => ({
                name: equipment.name,
                path: equipment.path,
                params: equipment.params
            })))
        }
    ))

    await fetch(
        "http://localhost:8000/workspace/start_experiments",
        {
            method: "POST",
            body: JSON.stringify(
                {
                    experiments: $state.snapshot(Object.values(gstore.experiments).map((experiment) => ({
                        name: experiment.name,
                        path: experiment.path,
                        params: experiment.params
                    }))),
                    equipments: $state.snapshot(Object.values(gstore.equipments).map((equipment) => ({
                        name: equipment.name,
                        path: equipment.path,
                        params: equipment.params
                    })))
                }
            ),
            headers: {
                "Content-type": "application/json"
            }
        }
    )

}