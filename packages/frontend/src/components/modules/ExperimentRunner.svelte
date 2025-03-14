<script lang="ts">
	import Play from "$icons/Play.svelte";

	import { gstore } from "$states/global.svelte";
	import type { Experiment } from "qoslab-shared";
	import Progress from "./Progress.svelte";

	let runnable_experiments = $derived(
		Object.values(gstore.experiments).filter(
			(experiment) =>
				experiment.created &&
				experiment.name &&
				experiment.name.length > 0 &&
				JSON.stringify(experiment.params) ===
					JSON.stringify(experiment.temp_params) &&
				experiment.params !== undefined
		) as Extract<Experiment, { created: true }>[]
	);
</script>

<div class="col-2 min-h-0 overflow-y-scroll w-full">
	{#each runnable_experiments as experiment}
		<div class="section bg-slate-200 row-1 justify-between w-full">
			<div class="w-32">
				<div class="wrapped bg-white w-fit">
					{experiment.name}
				</div>
			</div>
			<!-- <Progress /> -->
			<button
				class="icon-btn-sm green"
				onclick={async () => {
					// await startExperiments();
				}}><Play /></button>
		</div>
	{/each}
</div>
