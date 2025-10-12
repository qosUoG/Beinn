<script lang="ts">
	import { dependency_controller } from "$controllers/dependency.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import DependencyItem from "./DependencyItem.svelte";
	import NewDependency from "./NewDependency.svelte";
</script>

<div class="justify-between fcol-2 min-h-0 h-full bg-slate-200 rounded p-2">
	<div class="fcol-2">
		<div class="title">Dependency</div>
		<div class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2">
			{#each dependency_controller.dependencies as dependency}
				<DependencyItem bind:dependency />
			{/each}
		</div>
	</div>

	<NewDependency />
</div>
