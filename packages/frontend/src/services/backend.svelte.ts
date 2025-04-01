
import { gstore } from "$states/global.svelte";
import type { Dependency } from "qoslab-shared";
import { backendUrl, postRequestJsonInOut } from "./utils";

export async function disconnectWorkspace() {
    await fetch(backendUrl("workspace/disconnect"))
}

export async function setWorkspaceDirectory(path: string): Promise<void> {
    await postRequestJsonInOut(backendUrl("workspace/set"), { path: gstore.workspace.path })
}

export async function addDependency(source: string): Promise<void> {
    await postRequestJsonInOut(backendUrl("workspace/dependency/add"), { source, path: gstore.workspace.path })
}

export async function removeDependency(name: string): Promise<void> {
    return await postRequestJsonInOut(backendUrl("workspace/dependency/remove"), { name, path: gstore.workspace.path })
}

export async function readAllUvDependencies(): Promise<Dependency[]> {
    return (await postRequestJsonInOut(backendUrl("workspace/dependency/read_all"), { path: gstore.workspace.path }) as { dependencies: Dependency[] }).dependencies
}

// export async function readUvDependency(name: string): Promise<Dependency> {
//     return (await postRequestJsonInOut(backendUrl("workspace/dependency/read"), { name, path: gstore.workspace.path }) as { dependency: Dependency }).dependency
// }

export async function checkDependencyInit(directory: string): Promise<{ success: boolean }> {
    return await postRequestJsonInOut(backendUrl("workspace/dependency/check_init"), { directory, path: gstore.workspace.path })
}