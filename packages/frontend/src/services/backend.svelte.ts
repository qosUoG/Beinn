


import type { DependencyT, DependencyT_Installed } from "$states/dependency.svelte";
import type { Save } from "$states/workspace.svelte";
import { backendUrl, getRequestJsonOut, postRequestJsonInOut } from "./utils";

export async function backendDisconnectWorkspace() {
    return await getRequestJsonOut(backendUrl("workspace/disconnect"))
}

export async function backendLoadWorkspace(payload: { path: string }): Promise<Save | undefined> {
    // This shall return a state template
    return await postRequestJsonInOut(backendUrl("workspace/load"), payload)
}

export async function backendInstallDependency(payload: { install_string: string, path: string }): Promise<DependencyT_Installed> {
    return await postRequestJsonInOut(backendUrl("workspace/dependency/install"), payload)
}

export async function backendRemoveDependency(payload: { name: string, path: string }) {
    await postRequestJsonInOut(backendUrl("workspace/dependency/remove"), payload)
}

export async function backendReadAllUvDependencies(payload: { path: string }): Promise<DependencyT[]> {
    return await postRequestJsonInOut(backendUrl("workspace/dependency/read_all"), payload)
}


export async function backendCheckDependencyInit(payload: { directory: string, path: string }) {
    await postRequestJsonInOut(backendUrl("workspace/dependency/check_init"), payload)
}

export async function backendSaveWorkspace(payload: { path: string, save: Save }) {
    await postRequestJsonInOut(backendUrl("workspace/save"), payload)
}

