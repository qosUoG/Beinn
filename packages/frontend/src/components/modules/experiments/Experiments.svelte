<script>
	import ExperimentList from "$components/modules/experiments/ExperimentList.svelte";
	import { gstore } from "$states/global.svelte";
	import Chart from "./Chart.svelte";
</script>

<div class="w-full min-h-0 row-4">
	<ExperimentList />
	<div class="section bg-slate-200 flex-grow">
		{#each Object.values(gstore.experiments) as { chart_configs, id }}
			{#each Object.values(chart_configs) as chart_config}
				<div class="grid grid-cols-2 w-full">
					<Chart {chart_config} {id} />
				</div>
			{/each}
		{/each}
	</div>
</div>
