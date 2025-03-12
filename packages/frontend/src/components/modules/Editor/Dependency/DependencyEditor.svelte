<script lang="ts">
	import Trash from "$icons/Trash.svelte";
	import { gstore } from "$states/global.svelte";
	import type { Dependency, DependencySource } from "qoslab-shared";

	import { dependency_editor } from "./DependencyEditorController.svelte";

	import { autofocus, cn, timeoutLoop } from "$components/utils.svelte";
	import Download from "$icons/Download.svelte";
	import {
		addDependency,
		checkDependencyInit,
		readAllUvDependencies,
		removeDependency,
	} from "$services/backend.svelte";

	import LabelField from "$components/reuseables/Fields/LabelField.svelte";
	import FixedField from "$components/reuseables/Fields/FixedField.svelte";
	import SelectField from "$components/reuseables/Fields/SelectField.svelte";
	import SelfToggle from "$components/reuseables/SelfToggle.svelte";

	const dependency: Dependency | undefined = $derived.by(() => {
		if (dependency_editor.id === undefined) return undefined;

		return gstore.workspace.dependencies[dependency_editor.id];
	});

	let temp_source: DependencySource = $state({ type: "pip", package: "" });

	const type_options = ["local", "path", "git", "pip"];

	async function handleRemoveDependency() {
		if (dependency?.confirmed && dependency.source?.type !== "local")
			// TODO remove dependency in python project
			await removeDependency(dependency.name!);

		delete gstore.workspace.dependencies[dependency_editor.id!];

		dependency_editor.id = undefined;
	}

	async function handleAddDependency() {
		let source = "";
		switch (temp_source.type) {
			case "local":
				// Check init is available
				const { success } = await checkDependencyInit(
					temp_source.directory
				);
				console.log({ success });
				if (!success) return;

				// Write local to dependency
				gstore.workspace.dependencies[dependency_editor.id!] = {
					...gstore.workspace.dependencies[dependency_editor.id!],
					source: { ...temp_source },
					confirmed: true,
					name: temp_source.directory,
					fullname: temp_source.directory,
				};

				return;

			case "git":
				if (temp_source.git === "") return;
				source = temp_source.git;
				if (temp_source.branch) source += `@${temp_source.branch}`;
				if (temp_source.subdirectory)
					source += `#${temp_source.subdirectory}`;
				break;

			case "path":
				if (temp_source.path === "") return;
				source = temp_source.path;
				if (temp_source.editable) source += " --editable";
				break;
			case "pip":
				if (temp_source.package === "") return;
				source = temp_source.package;
				break;
		}

		await addDependency(source);

		temp_source = { type: "pip", package: "" };

		const current_dependency_names = Object.values(
			$state.snapshot(gstore.workspace.dependencies)
		)
			.filter((d) => d.confirmed)
			.map((d) => d.name);

		// Read All dependencies and figure out which is the new one
		const allDependencies = await readAllUvDependencies();

		Object.values(allDependencies.filter((d) => d.confirmed)).forEach(
			(d) => {
				if (!current_dependency_names.includes(d.name)) {
					gstore.workspace.dependencies[dependency_editor.id!] = {
						...d,
						id: dependency_editor.id!,
					};
				}
			}
		);
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
					<div class="row-2">
						<SelectField
							key="Type"
							bind:value={temp_source.type}
							options={type_options} />
						{#if temp_source.type === "path"}
							<SelfToggle
								key="editable"
								bind:value={temp_source.editable} />
						{/if}
						<button
							class="icon-btn-sm green"
							onclick={handleAddDependency}><Download /></button>
					</div>

					{#if temp_source.type === "pip"}
						<LabelField key="Package Name">
							<input
								type="text"
								class="flex-grow"
								bind:value={temp_source.package}
								onfocus={autofocus} />
						</LabelField>
					{:else if temp_source.type === "git"}
						<LabelField key="Url">
							<input
								type="text"
								class="flex-grow"
								bind:value={temp_source.git}
								onfocus={autofocus} />
						</LabelField>
						<LabelField key="Branch">
							<input
								type="text"
								class="flex-grow"
								bind:value={temp_source.branch}
								onfocus={autofocus} />
						</LabelField>

						<LabelField key="Subdirectory">
							<input
								type="text"
								class="flex-grow"
								bind:value={temp_source.subdirectory}
								onfocus={autofocus} />
						</LabelField>
					{:else if temp_source.type === "path"}
						<LabelField key="Path">
							<input
								type="text"
								class="flex-grow"
								bind:value={temp_source.path}
								onfocus={autofocus} />
						</LabelField>
					{:else if temp_source.type === "local"}
						<LabelField key="Directory">
							<input
								type="text"
								class="flex-grow"
								bind:value={temp_source.directory}
								onfocus={autofocus} />
						</LabelField>
					{/if}
				{:else if dependency.source!.type === "pip"}
					<!-- All Following has as confirmed dependency -->
					<FixedField key="Package" value={dependency.fullname} />
				{:else if dependency.source!.type === "git"}
					<FixedField key="Git Path" value={dependency.source.git} />
					{#if dependency.source!.subdirectory}
						<FixedField
							key="Subdirectory"
							value={dependency.source.subdirectory} />
					{/if}
				{:else if dependency.source!.type === "path"}
					<FixedField key="Path" value={dependency.source.path} />
				{:else if dependency.source!.type === "local"}
					<FixedField key="Local Directory" value={dependency.name} />
				{/if}
			</div>
		{/if}
	</div>
{/key}
