<script lang="ts">
	import ExperimentList from "$components/modules/experiments/ExperimentList.svelte";
	import { gstore } from "$states/global.svelte";
	import Chart from "./Chart.svelte";

	let relative_parent: HTMLDivElement;
</script>

<div class="w-full min-h-0 frow-4">
	<ExperimentList />
	<div
		class="section bg-slate-200 flex-grow relative overflow-scroll scrollbar"
		bind:this={relative_parent}
	>
		{#each Object.values(gstore.experiments) as { chart_configs, id }}
			{#each Object.values(chart_configs) as chart_config}
				<Chart {chart_config} {id} {relative_parent} />
			{/each}
		{/each}
	</div>
</div>
