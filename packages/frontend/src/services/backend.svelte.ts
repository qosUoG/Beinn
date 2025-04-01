
import { gstore, type Save } from "$states/global.svelte";
import type { ConfirmedDependency, Dependency } from "qoslab-shared";
import { backendUrl, postRequestJsonInOut } from "./utils";

export async function disconnectWorkspace() {
    await fetch(backendUrl("workspace/disconnect"))
}

export async function loadWorkspace(): Promise<{ save: undefined | Save }> {
    // This shall return a state template
    return await postRequestJsonInOut(backendUrl("workspace/load"), { path: gstore.workspace.path })


}

export async function addDependency(source: string): Promise<void> {
    await postRequestJsonInOut(backendUrl("workspace/dependency/add"), { source, path: gstore.workspace.path })

}

export async function removeDependency(name: string): Promise<void> {
    return await postRequestJsonInOut(backendUrl("workspace/dependency/remove"), { name, path: gstore.workspace.path })
}

export async function readAllUvDependencies(): Promise<ConfirmedDependency[]> {
    return (await postRequestJsonInOut(backendUrl("workspace/dependency/read_all"), { path: gstore.workspace.path }) as { dependencies: ConfirmedDependency[] }).dependencies
}

// export async function readUvDependency(name: string): Promise<Dependency> {
//     return (await postRequestJsonInOut(backendUrl("workspace/dependency/read"), { name, path: gstore.workspace.path }) as { dependency: Dependency }).dependency
// }

export async function checkDependencyInit(directory: string): Promise<{ success: boolean }> {
    return await postRequestJsonInOut(backendUrl("workspace/dependency/check_init"), { directory, path: gstore.workspace.path })
}

export async function saveWorkspace() {
    const save: Save = {
        dependencies: gstore.workspace.dependencies,
        equipments: gstore.equipments,
        experiments: gstore.experiments,

    }
    await postRequestJsonInOut(backendUrl("workspace/save"), { path: gstore.workspace.path, payload: save })
}

