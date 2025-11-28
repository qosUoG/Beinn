<script lang="ts">
	import { cn } from "$components/utils.svelte";

	import {
		dependency_controller,
		type DependencySource,
	} from "$controllers/dependency.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import { Plus } from "@lucide/svelte";
	import InputField from "$components/fields/InputField.svelte";
	import TabSelect from "$components/fields/TabSelect.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { equipment_controller } from "$controllers/equipment.svelte";
	import { tick } from "svelte";

	let source: DependencySource = $state({
		type: "pip",
		package: "",
	});

	async function install() {
		await dependency_controller.install({
			path: workspace_controller.path!,
			source,
		});
		switch (source.type) {
			case "pip":
				source = { type: "pip", package: "" };
				break;
			case "git":
				source = {
					type: "git",
					git: "",
					branch: "",
					subdirectory: "",
				};
				break;
			case "path":
				source = {
					type: "path",
					path: "",
					editable: source.editable,
				};
				break;
		}

		await dependency_controller.saveToDisk();
		await tick();
		await Promise.all([
			equipment_controller.updateImports(),
			experiment_controller.updateImports(),
		]);
	}
</script>

<div class="bg-white rounded p-1 pb-2 fcol min-h-[125px]">
	<div class="title text-center wrapped relative mb-1">
		New Dependency

		{#if experiment_controller.editable}
			<button
				class="absolute right-0 top-0 flex items-center h-full bg-blue-600 rounded aspect-square justify-center icon-btn-sm text-white"
				aria-label="Add dependency"
				onclick={install}
			>
				<Plus />
			</button>
		{:else}
			<span
				class="absolute right-0 top-0 flex items-center h-full bg-slate-300 rounded aspect-square justify-center icon-btn-sm text-white"
			>
				<Plus />
			</span>
		{/if}
	</div>
	{#snippet typeBoilerPlate(type: "pip" | "git" | "path")}
		<button
			class={cn(
				" border-slate-400   py-0.5",
				source.type === type ? "bg-slate-300 font-semibold " : "",
			)}
			onclick={() => {
				switch (type) {
					case "pip":
						source = { type: "pip", package: "" };
						break;
					case "git":
						source = {
							type: "git",
							git: "",
							branch: "",
							subdirectory: "",
						};
						break;
					case "path":
						source = { type: "path", path: "", editable: false };
						break;
				}
			}}>{type}</button
		>
	{/snippet}
	<div
		class="fcol *:border *:border-slate-400 *:border-b-0 last:border-b last:border-b-slate-400"
	>
		<div class="frow items-stretch">
			<div class="min-w-16 px-1 h-full flex items-center">
				type<span class="text-red-500">*</span>
			</div>
			<div class="grid grid-cols-3 grow *:border-l *:border-slate-400">
				{@render typeBoilerPlate("pip")}
				{@render typeBoilerPlate("git")}
				{@render typeBoilerPlate("path")}
			</div>
		</div>

		{#if source.type === "pip"}
			<InputField label="package" bind:value={source.package} mandatory />
		{:else if source.type === "git"}
			<InputField
				label="url"
				bind:value={source.git}
				placeholder="https:// ... (without .git)"
				mandatory
			/>
			<InputField label="branch" bind:value={source.branch} />
			<InputField label="subdirectory" bind:value={source.subdirectory} />
		{:else if source.type === "path"}
			<InputField label="path" bind:value={source.path} mandatory />
			<TabSelect
				label="editable"
				bind:value={source.editable}
				items={[
					{ key: "True", value: true },
					{ key: "False", value: false },
				]}
				mandatory
			/>
		{/if}
	</div>
</div>
