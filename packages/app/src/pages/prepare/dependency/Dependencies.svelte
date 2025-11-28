<script lang="ts">
	import { dependency_controller } from "$controllers/dependency.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import { ArrowBigUpDash, LoaderCircle } from "@lucide/svelte";
	import DependencyItem from "./DependencyItem.svelte";
	import NewDependency from "./NewDependency.svelte";
	import { tick } from "svelte";
	import { equipment_controller } from "$controllers/equipment.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";

	async function update() {
		for (const dependency of dependency_controller.dependencies) {
			await dependency_controller.update({
				name: dependency.name,
			});
			await dependency_controller.saveToDisk();
			await tick();
		}
		await Promise.all([
			equipment_controller.updateImports(),
			experiment_controller.updateImports(),
		]);
	}
</script>

<div class="justify-between fcol-2 min-h-0 grow bg-slate-200 rounded p-2">
	<div class="fcol-2 grow min-h-0">
		<div class="frow justify-between items-center">
			<div class="title">Dependency</div>
			{#if workspace_controller.status === "ready"}
				{#if dependency_controller.has_updating_package}
					<div class="icon-btn-sm bg-blue-600">
						<div class="text-white animate-spin">
							<LoaderCircle />
						</div>
					</div>
				{:else if experiment_controller.editable}
					<button
						class=" icon-btn-sm text-white bg-blue-600"
						onclick={update}
					>
						<ArrowBigUpDash />
					</button>
				{/if}
			{/if}
		</div>
		<div
			class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2 grow pb-8"
		>
			{#if workspace_controller.status === "ready"}
				{#each dependency_controller.dependencies as dependency}
					<DependencyItem bind:dependency />
				{/each}
			{/if}
		</div>
	</div>

	{#if workspace_controller.status === "ready"}
		<NewDependency />
	{/if}
</div>
