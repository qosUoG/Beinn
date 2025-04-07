<script lang="ts">
	import ExperimentList from "$components/modules/runtime/ExperimentList.svelte";
	import { gstore } from "$states/global.svelte";
	import Chart from "./Chart.svelte";

	let relative_parent: HTMLDivElement;
</script>

<div class="w-full min-h-0 frow-4">
	<ExperimentList />
	<div
		class="section bg-slate-200 flex-grow relative overflow-scroll scrollbar-slate-400"
		bind:this={relative_parent}>
		{#each Object.values(gstore.workspace.experiments.experiments) as { charts, id }}
			{#each Object.values(charts.charts) as chart}
				<Chart {chart} {id} {relative_parent} />
			{/each}
		{/each}
	</div>
</div>
