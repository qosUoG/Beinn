<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import {
		dependency_controller,
		type Dependency,
	} from "$controllers/dependency.svelte";
	import { equipment_controller } from "$controllers/equipment.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { beinn_log_controller } from "$controllers/log.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import { Trash2 } from "@lucide/svelte";
	import { tick } from "svelte";

	let { dependency = $bindable() }: { dependency: Dependency } = $props();
</script>

<div class="bg-slate-50 rounded p-1 fcol-1">
	<div class="flex items-center w-full justify-between">
		<div class=" text-slate-950 font-medium wrapped px-0">
			{dependency.name}
		</div>
		<div class=" frow-1">
			<button
				class={cn(
					dependency.has_driver
						? "bg-green-600 border-green-600 text-white"
						: "text-slate-600 border-slate-600 line-through",
					"border rounded px-1 box-border"
				)}
				onclick={async () => {
					dependency.has_driver = !dependency.has_driver;
					await tick();
					equipment_controller.updateImports();
					experiment_controller.updateImports();
				}}>
				Driver / Script
			</button>
			<button
				aria-label="Remove dependency"
				class="bg-red-600 icon-btn-sm text-white"
				onclick={async () => {
					if (!workspace_controller.path) {
						beinn_log_controller.append(
							"Cannot uninstall dependency: No workspace connected."
						);
						return;
					}
					dependency_controller.uninstallDependency({
						name: dependency.name,
						path: workspace_controller.path,
					});
				}}>
				<Trash2 />
			</button>
		</div>
	</div>
	<div class="fcol gap-0.5">
		{#if dependency.source.type === "git"}
			<div class="text-slate-950/75">
				Git: {dependency.source.git}
			</div>
			<div class="text-slate-950/75">
				Branch: {dependency.source.branch}
			</div>
			<div class="text-slate-950/75">
				Subdirectory: {dependency.source.subdirectory}
			</div>
		{:else if dependency.source.type === "path"}
			<div class="text-slate-950/75">
				Path: {dependency.source.path}
			</div>
			<div class="text-slate-950/75">
				{dependency.source.editable ? "Editable" : "Not editable"}
			</div>
		{:else if dependency.source.type === "pip"}
			<div class="text-slate-950/75">
				Pip: {dependency.fullname}
			</div>
		{/if}
	</div>
</div>
