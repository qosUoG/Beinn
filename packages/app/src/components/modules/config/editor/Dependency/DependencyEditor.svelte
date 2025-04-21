<script lang="ts">
	import Trash from "$icons/Trash.svelte";

	import { dependency_editor } from "./DependencyEditorController.svelte";

	import { autofocus } from "$components/utils.svelte";
	import Download from "$icons/Download.svelte";

	import LabelField from "$components/reuseables/Fields/LabelField.svelte";
	import FixedField from "$components/reuseables/Fields/FixedField.svelte";
	import SelectField from "$components/reuseables/Fields/SelectField.svelte";
	import SelfToggle from "$components/reuseables/SelfToggle.svelte";
	import { tick } from "svelte";
	import { workspace } from "$states/workspace.svelte";

	const dependency = $derived(
		workspace.dependencies.dependencies[dependency_editor.id!]
	);

	let temp_type: "local" | "path" | "git" | "pip" = $state("pip");

	$effect(() => {
		if (dependency && !dependency.installed)
			switch (temp_type) {
				case "pip":
					dependency.source = { type: "pip", package: "" };
					break;
				case "git":
					dependency.source = {
						type: "git",
						git: "",
						subdirectory: "",
						branch: "",
					};
					break;
				case "local":
					dependency.source = {
						type: "local",
						directory: "",
					};
					break;
				case "path":
					dependency.source = {
						type: "path",
						path: "",
						editable: false,
					};
					break;
			}
	});

	const type_options = ["local", "path", "git", "pip"];

	async function handleRemove() {
		await dependency.uninstall();
		dependency_editor.id = undefined;
	}

	async function handleAddDependency() {
		await dependency.install();

		await tick();
		console.log(dependency.installed);
	}
</script>

{#if dependency_editor.id && dependency}
	{#key dependency_editor.id}
		<div class="section bg-slate-200 col-span-2">
			<div class="fcol-2">
				<div class="frow justify-between items-end">
					<div class="title bg-white wrapped">
						Editor - Dependency
					</div>
					<button class="icon-btn-sm red" onclick={handleRemove}
						><Trash /></button>
				</div>

				{#if !dependency.installed}
					<div class="frow-2">
						<SelectField
							key="Type"
							bind:value={temp_type}
							options={type_options} />
						{#if dependency.source.type === "path"}
							<SelfToggle
								key="editable"
								bind:value={dependency.source.editable} />
						{/if}
						<button
							class="icon-btn-sm green"
							onclick={handleAddDependency}><Download /></button>
					</div>

					{#if dependency.source.type === "pip"}
						<LabelField key="Package Name">
							<input
								type="text"
								class="flex-grow"
								bind:value={dependency.source.package}
								onfocus={autofocus} />
						</LabelField>
					{:else if dependency.source.type === "git"}
						<LabelField key="Url">
							<input
								type="text"
								class="flex-grow"
								bind:value={dependency.source.git}
								onfocus={autofocus} />
						</LabelField>
						<LabelField key="Branch">
							<input
								type="text"
								class="flex-grow"
								bind:value={dependency.source.branch}
								onfocus={autofocus} />
						</LabelField>

						<LabelField key="Subdirectory">
							<input
								type="text"
								class="flex-grow"
								bind:value={dependency.source.subdirectory}
								onfocus={autofocus} />
						</LabelField>
					{:else if dependency.source.type === "path"}
						<LabelField key="Path">
							<input
								type="text"
								class="flex-grow"
								bind:value={dependency.source.path}
								onfocus={autofocus} />
						</LabelField>
					{:else if dependency.source.type === "local"}
						<LabelField key="Directory">
							<input
								type="text"
								class="flex-grow"
								bind:value={dependency.source.directory}
								onfocus={autofocus} />
						</LabelField>
					{/if}
				{:else if dependency.source.type === "pip"}
					{console.log(dependency)}
					<!-- All Following has as confirmed dependency -->
					<FixedField key="Package" value={dependency.fullname} />
				{:else if dependency.source.type === "git"}
					<FixedField key="Git Path" value={dependency.source.git} />
					{#if dependency.source.subdirectory}
						<FixedField
							key="Subdirectory"
							value={dependency.source.subdirectory} />
					{/if}
				{:else if dependency.source.type === "path"}
					<FixedField key="Path" value={dependency.source.path} />
				{:else if dependency.source.type === "local"}
					{console.log(dependency.source.type)}
					<FixedField key="Local Directory" value={dependency.name} />
				{/if}
			</div>
		</div>
	{/key}
{/if}
