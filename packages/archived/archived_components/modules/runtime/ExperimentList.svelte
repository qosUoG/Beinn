<script lang="ts">
	import { workspace } from "$states/workspace.svelte";
	import ExperimentListItem from "./ExperimentListItem.svelte";
</script>

<div class="fcol-2 w-96 section bg-slate-200 h-full min-h-0">
	<div class="title wrapped bg-white w-fit">Experiments</div>
	<div class="h-full overflow-y-scroll fcol-2 min-h-0">
		{#each Object.values(workspace.experiments.experiments).filter( (e) => e.isRunnable() ) as { id }}
			<ExperimentListItem
				bind:experiment={workspace.experiments.experiments[id]} />
		{/each}
	</div>
</div>
