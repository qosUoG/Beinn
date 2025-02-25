import type { Directory } from "qoslab-shared";

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

export async function addDependency(path: string): Promise<void> {
    await fetch(
        "http://localhost:4000/workspace/add_dependency",
        {
            method: "POST",
            body: JSON.stringify({ path }),
            headers: {
                "Content-type": "application/json"
            },
        }
    )
}