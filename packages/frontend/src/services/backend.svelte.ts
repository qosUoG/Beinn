import { getRandomId } from "$lib/utils";
import type { Dependency, Directory } from "qoslab-shared";

export async function setWorkspaceDirectory(path: string): Promise<Directory> {
    console.log("here")
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

export async function addDependency(identifier: string): Promise<void> {
    await fetch(
        "http://localhost:4000/workspace/add_dependency",
        {
            method: "POST",
            body: JSON.stringify({ identifier }),
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
            body: JSON.stringify({ name }),
            headers: {
                "Content-type": "application/json"
            },
        }
    )
}

export async function readDependency(): Promise<Record<string, Dependency>> {
    const res = await (await fetch("http://localhost:4000/workspace/read_dependency")).json() as { dependencies: Dependency[] }

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