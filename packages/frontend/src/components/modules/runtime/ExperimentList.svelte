<script lang="ts">
	import { gstore } from "$states/global.svelte";

	import ExperimentListItem from "./ExperimentListItem.svelte";
</script>

<div class="fcol-2 w-96 section bg-slate-200 h-full min-h-0">
	<div class="title wrapped bg-white w-fit">Experiments</div>
	<div class="h-full overflow-y-scroll fcol-2 min-h-0">
		{#each gstore.workspace.experiments.runnables as _, i}
			<ExperimentListItem
				bind:experiment={gstore.workspace.experiments.runnables[i]} />
		{/each}
	</div>
</div>
