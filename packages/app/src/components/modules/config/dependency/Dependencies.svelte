<script lang="ts">
	import { dependency_controller } from "$controllers/DependencyController.svelte";
	import { workspace_controller } from "$controllers/WorkspaceController.svelte";
	import DependencyItem from "./DependencyItem.svelte";
	import NewDependency from "./NewDependency.svelte";
</script>

{#if workspace_controller.connected}
	<div class="justify-between fcol-2 min-h-0 h-full">
		<div class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2">
			{#each dependency_controller.dependencies as dependency}
				<DependencyItem bind:dependency />
			{/each}
		</div>

		<NewDependency />
	</div>
{/if}
