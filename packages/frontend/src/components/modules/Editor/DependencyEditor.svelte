<script lang="ts">
	import Trash from "$icons/Trash.svelte";
	import { gstore } from "$states/global.svelte";
	import type { Dependency } from "qoslab-shared";

	import { dependency_editor } from "./DependencyEditorController.svelte";

	import Separator from "./Separator.svelte";
	import { autofocus, timeoutLoop } from "$components/utils.svelte";
	import Download from "$icons/Download.svelte";
	import {
		addDependency,
		checkDependencyInit,
		readAllUvDependencies,
		removeDependency,
	} from "$services/backend.svelte";
	import { getRandomId } from "$lib/utils";

	const dependency: Dependency | undefined = $derived.by(() => {
		if (dependency_editor.id === undefined) return undefined;

		return gstore.workspace.dependencies[dependency_editor.id];
	});

	let temp_source = $state("");

	async function handleRemoveDependency() {
		if (dependency?.confirmed && dependency.source?.type !== "local")
			// TODO remove dependency in python project
			await removeDependency(dependency.name!);

		delete gstore.workspace.dependencies[dependency_editor.id!];

		dependency_editor.id = undefined;
	}

	async function handleAddDependency() {
		// Do nothing if the temp_source is invalid
		if (temp_source === undefined || temp_source === "") return;

		// Special headling for the python modules within project directory
		if (temp_source.startsWith("local:")) {
			const res = temp_source.split(":");
			if (res.length > 2) return;

			const name = res[1];

			// Check init is available
			const { success } = await checkDependencyInit(name);
			if (!success) return;

			// Write local to dependency
			gstore.workspace.dependencies[dependency_editor.id!] = {
				...gstore.workspace.dependencies[dependency_editor.id!],
				source: { type: "local" },
				confirmed: true,
				name,
				fullname: `local:${name}`,
			};

			return;
		}

		// Add as git / path / pip package
		// TODO: Error Handling
		await addDependency(temp_source);

		temp_source = "";

		const current_dependency_names = Object.values(
			$state.snapshot(gstore.workspace.dependencies)
		).map((d) => d.name);

		// Keep Retrying in case there is a time gap between running add dependency
		// and actual pyproject.toml update
		timeoutLoop(5 * 1000, async () => {
			let _continue = true;

			// Read All dependencies and figure out which is the new one
			let allDependencies = await readAllUvDependencies();

			Object.values(allDependencies).forEach((d) => {
				if (!current_dependency_names.includes(d.name)) {
					const id = getRandomId(
						Object.keys(gstore.workspace.dependencies)
					);
					gstore.workspace.dependencies[id] = { ...d, id };
					dependency_editor.id = id;

					_continue = false;
				}
			});

			return _continue;
		});
	}
</script>

{#key dependency_editor.id}
	<div class="container bg-slate-200 col-span-2">
		{#if dependency !== undefined}
			<div class="col-2">
				<div class="row justify-between items-end">
					<div class="title bg-white wrapped">
						Editor - Dependency
					</div>
					<button
						class="icon-btn-sm red"
						onclick={handleRemoveDependency}><Trash /></button>
				</div>

				{#if !dependency.confirmed}
					<div class="row-2 w-full">
						<label class="row-2 bg-white wrapped w-full flex-grow">
							<div class="editor-label">Source</div>
							<Separator />
							<input
								type="text"
								class="flex-grow"
								bind:value={temp_source}
								onfocus={autofocus} />
						</label>

						<button
							class="icon-btn-sm green"
							onclick={handleAddDependency}><Download /></button>
					</div>
				{:else if dependency.source!.type === "pip"}
					<!-- All Following has as confirmed dependency -->
					<div class="row-2 bg-white wrapped w-full">
						<div class="editor-label">Package</div>
						<Separator />
						<div class="">
							{dependency.fullname}
						</div>
					</div>
				{:else if dependency.source!.type === "git"}
					<div class="row-2 bg-white wrapped w-full">
						<div class="editor-label">Git Path</div>
						<Separator />
						<div class="">
							{dependency.source!.git}
						</div>
					</div>
					{#if dependency.source!.subdirectory}
						<div class="row-2 bg-white wrapped w-full">
							<div class="editor-label">Subdirectory</div>
							<Separator />
							<div class="">
								{dependency.source!.subdirectory}
							</div>
						</div>
					{/if}
				{:else if dependency.source!.type === "path"}
					<div class="row-2 bg-white wrapped w-full">
						<div class="editor-label">Path</div>
						<Separator />
						<div class="">
							{dependency.source!.path}
						</div>
					</div>
				{:else if dependency.source!.type === "local"}
					<div class="row-2 bg-white wrapped w-full">
						<div class="editor-label">Local</div>
						<Separator />
						<div class="">
							{dependency.name}
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>
{/key}
