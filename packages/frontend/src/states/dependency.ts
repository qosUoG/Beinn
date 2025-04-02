import { checkDependencyInit } from "$services/backend.svelte";
import type { DependencySource, Result } from "qoslab-shared";
import { gstore } from "./global.svelte";

export async function addDependency({ id, source }: { id: string, source: DependencySource }): Promise<Result> {
    // Resolve the source
    switch (source.type) {
        case "local":
            // Check init is available
            const { success } = await checkDependencyInit(
                source.directory
            );

            if (!success) return { success: false };

            // Write local to dependency
            gstore.workspace.dependencies[id] = {
                ...gstore.workspace.dependencies[id],
                source: { ...source },
                confirmed: true,
                name: source.directory,
                fullname: source.directory,
                add_string: source.directory,
            };
            break;

        case "git":
            if (source.git === "") return;
            source = source.git;
            if (source.branch) source += `@${source.branch}`;
            if (source.subdirectory)
                source += `#${source.subdirectory}`;
            break;

        case "path":
            if (source.path === "") return;
            source = source.path;
            if (source.editable) source += " --editable";
            break;
        case "pip":
            if (source.package === "") return;
            source = source.package;
            break;
    }

    // Add dependency with uv id not local
    if (source.type !== "local") {
        await addDependency(source);

        source = { type: "pip", package: "" };

        const current_dependency_names = Object.values(
            $state.snapshot(gstore.workspace.dependencies)
        )
            .filter((d) => d.confirmed)
            .map((d) => d.name);

        // Read All dependencies and figure out which is the new one
        const allDependencies = await readAllUvDependencies();

        Object.values(allDependencies).forEach((d) => {
            if (!current_dependency_names.includes(d.name)) {
                gstore.workspace.dependencies[id] = {
                    ...d,
                    id: id,
                    add_string: source,
                };
            }
        });
    }
}