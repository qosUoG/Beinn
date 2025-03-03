import { getRandomId } from "$lib/utils";
import { gstore } from "$states/global.svelte";
import type { Dependency, Directory } from "qoslab-shared";

export async function setWorkspaceDirectory(path: string): Promise<Directory> {

    return await (
        await fetch(
            "http://localhost:4000/workspace/set_directory",
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

export async function addDependency(source: string): Promise<void> {
    await fetch(
        "http://localhost:4000/workspace/add_dependency",
        {
            method: "POST",
            body: JSON.stringify({ source, path: gstore.workspace.path }),
            headers: {
                "Content-type": "application/json"
            },
        }
    )
}

export async function removeDependency(name: string): Promise<void> {
    await fetch(
        "http://localhost:4000/workspace/remove_dependency",
        {
            method: "POST",
            body: JSON.stringify({ name, path: gstore.workspace.path }),
            headers: {
                "Content-type": "application/json"
            },
        }
    )
}

export async function readDependency(): Promise<Record<string, Dependency>> {
    const res = await (await fetch("http://localhost:4000/workspace/read_dependency", { method: "POST", body: JSON.stringify({ path: gstore.workspace.path }) })).json() as { dependencies: Dependency[] }

    let dependencies: Record<string, Dependency> = {}

    for (const dependency of res.dependencies) {

        const id = getRandomId(Object.keys(dependencies))
        dependencies[id] = {
            ...dependency,
            id,
        }
    }

    return dependencies


}

