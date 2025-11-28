<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import {
		dependency_controller,
		type Dependency,
	} from "$controllers/dependency.svelte";
	import { equipment_controller } from "$controllers/equipment.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import { ArrowUp, LoaderCircle, Trash2 } from "@lucide/svelte";
	import { tick } from "svelte";

	let { dependency = $bindable() }: { dependency: Dependency } = $props();

	async function update() {
		await dependency_controller.update({
			name: dependency.name,
		});
		await dependency_controller.saveToDisk();
		await tick();
		await Promise.all([
			equipment_controller.updateImports(),
			experiment_controller.updateImports(),
		]);
	}

	async function uninstall() {
		await dependency_controller.uninstall({
			name: dependency.name,
			path: workspace_controller.path!,
		});
		await dependency_controller.saveToDisk();
		await tick();
		await Promise.all([
			equipment_controller.updateImports(),
			experiment_controller.updateImports(),
		]);
	}

	async function toggleDriver() {
		await dependency_controller.toggleDriver(dependency.name);
		await dependency_controller.saveToDisk();
		await tick();
		await Promise.all([
			equipment_controller.updateImports(),
			experiment_controller.updateImports(),
		]);
	}
</script>

<div class="bg-white rounded p-1 fcol-1">
	<div class="flex items-center w-full justify-between">
		<div
			class="  font-medium border-l-3 border-slate-400 pl-1 min-h-6 flex items-center"
		>
			{dependency.name}
		</div>
		{#if experiment_controller.editable}
			<div class=" frow-2">
				{#if dependency.updating}
					<div class="icon-btn-sm bg-blue-600">
						<div class="text-white animate-spin">
							<LoaderCircle />
						</div>
					</div>
				{:else}
					<button
						class={cn("icon-btn-sm text-white bg-blue-600")}
						onclick={update}
					>
						<ArrowUp />
					</button>
				{/if}
				<button
					class={cn(
						dependency.has_driver
							? " border-green-500 text-white bg-green-500"
							: "border-slate-500 text-slate-500 line-through",
						"border rounded px-1 box-border",
					)}
					onclick={toggleDriver}
				>
					Driver / Script
				</button>
				{#if !dependency.uninstalling}
					<button
						aria-label="Remove dependency"
						class="bg-red-600 icon-btn-sm text-white"
						onclick={uninstall}
					>
						<Trash2 />
					</button>
				{:else}
					<div class="bg-red-600 icon-btn-sm text-white">
						<div class="text-white animate-spin">
							<LoaderCircle />
						</div>
					</div>
				{/if}
			</div>
		{/if}
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
