<script lang="ts">
	import { gstore } from "$states/global.svelte";

	import ExperimentListItem from "./ExperimentListItem.svelte";

	$inspect(gstore.workspace.experiments.experiments);
</script>

<div class="fcol-2 w-96 section bg-slate-200 h-full min-h-0">
	<div class="title wrapped bg-white w-fit">Experiments</div>
	<div class="h-full overflow-y-scroll fcol-2 min-h-0">
		{#each Object.values(gstore.workspace.experiments.experiments).filter( (e) => e.isRunnable() ) as { id }}
			<ExperimentListItem
				bind:experiment={
					gstore.workspace.experiments.experiments[id]
				} />
		{/each}
	</div>
</div>
