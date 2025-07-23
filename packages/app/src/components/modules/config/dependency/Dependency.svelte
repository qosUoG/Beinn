<script lang="ts">
	import { dependencies } from "$controllers/DependencyController.svelte";
	import { workspace } from "$controllers/WorkspaceController.svelte";
	import DependencyItem from "./DependencyItem.svelte";
	import NewDependency from "./NewDependency.svelte";
</script>

{#if workspace.connected}
	<div class="justify-between fcol-2 min-h-0 h-full">
		<div class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2">
			{#each dependencies.dependencies as dependency}
				<DependencyItem {dependency} />
			{/each}
		</div>

		<NewDependency />
	</div>
{/if}
