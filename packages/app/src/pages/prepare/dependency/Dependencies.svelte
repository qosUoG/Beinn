<script lang="ts">
	import { dependency_controller } from "$controllers/dependency.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import DependencyItem from "./DependencyItem.svelte";
	import NewDependency from "./NewDependency.svelte";
</script>

<div class="justify-between fcol-2 min-h-0 flex-grow bg-slate-200 rounded p-2">
	<div class="fcol-2 flex-grow min-h-0">
		<div class="title">Dependency</div>
		<div
			class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2 flex-grow pb-8">
			{#if workspace_controller.status === "ready"}
				{#each dependency_controller.dependencies as dependency}
					<DependencyItem bind:dependency />
				{/each}
			{/if}
		</div>
	</div>

	<NewDependency />
</div>
