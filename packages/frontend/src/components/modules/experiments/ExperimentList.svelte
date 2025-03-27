<script lang="ts">
	import Play from "$icons/Play.svelte";

	import { gstore } from "$states/global.svelte";

	import Progress from "./Progress.svelte";
	import StopWatch from "$icons/StopWatch.svelte";
	import Rotate from "$icons/Rotate.svelte";

	import {
		continueExperiment,
		pauseExperiment,
		startExperiment,
		stopExperiment,
	} from "$services/qoslabapp.svelte";
	import type { CreatedRuntimeExperiment } from "$states/experiment";
	import Pause from "$icons/Pause.svelte";
	import Stop from "$icons/Stop.svelte";
	import Loader from "$icons/Loader.svelte";

	let runnable_experiments = $derived(
		Object.values(gstore.experiments).filter(
			(experiment) =>
				experiment.created &&
				experiment.name &&
				experiment.name.length > 0 &&
				JSON.stringify(experiment.params) ===
					JSON.stringify(experiment.temp_params) &&
				experiment.params !== undefined,
		) as CreatedRuntimeExperiment[],
	);

	function zeropad(num: number) {
		if (num < 10) return `0${num}`;
		return `${num}`;
	}
</script>

<div class="fcol-2 w-96 section bg-slate-200 h-full min-h-0">
	<div class="title wrapped bg-white w-fit">Experiments</div>
	<div class="h-full overflow-y-scroll fcol-2 min-h-0">
		{#each runnable_experiments as experiment}
			{console.log(experiment.chart_configs)}
			{@const iteration_time =
				experiment.total_time - experiment.iteration_time_start}

			<div class="section bg-white fcol-2 justify-between w-full">
				<div class="grid grid-cols-2">
					<div class="wrapped bg-slate-200 w-fit">
						{experiment.name}
					</div>
					<Progress {experiment} />
				</div>

				<div class="frow justify-between">
					<div class="frow-1">
						<div
							class="bg-slate-200 frow rounded items-center w-24"
						>
							<div class="icon-btn-sm">
								<StopWatch />
							</div>
							<div class="p-1 rounded pr-2 flex-grow text-center">
								{#if experiment.total_time >= 0 && experiment.proposed_total_iterations !== undefined}
									{@render timer(experiment.total_time)}
								{:else}
									-
								{/if}
							</div>
						</div>
						<div
							class="bg-slate-200 frow rounded items-center w-24"
						>
							<div class="icon-btn-sm">
								<Rotate />
							</div>
							<div class="p-1 rounded pr-2 flex-grow text-center">
								{#if iteration_time >= 0 && experiment.status !== "initial"}
									{@render timer(iteration_time)}
								{:else}
									-
								{/if}
							</div>
						</div>

						<div class="wrapped bg-slate-200 min-w-12 text-center">
							{#if experiment.iteration_count + 1 < 0 || experiment.proposed_total_iterations === undefined}
								-
							{:else}
								{experiment.iteration_count + 1}
							{/if}

							/ {#if experiment.proposed_total_iterations === undefined}
								-
							{:else if experiment.proposed_total_iterations === -1}
								∞
							{:else}
								{experiment.proposed_total_iterations}
							{/if}
						</div>
					</div>
					<div class="frow-1">
						{#if experiment.status === "initial" || experiment.status === "completed" || experiment.status === "stopped"}
							<button
								class="icon-btn-sm green"
								onclick={async () => {
									experiment.iteration_count = -1;
									experiment.status = "starting";
									await startExperiment(experiment);
								}}><Play /></button
							>
						{:else if experiment.status === "continuing" || experiment.status === "started" || experiment.status === "starting" || experiment.status === "continued"}
							<button
								class="icon-btn-sm red"
								onclick={async () => {
									experiment.status = "pausing";
									await pauseExperiment(experiment);
								}}><Pause /></button
							>
						{:else if experiment.status === "paused" || experiment.status === "pausing"}
							<button
								class="icon-btn-sm red"
								onclick={async () => {
									experiment.status = "stopping";
									await stopExperiment(experiment);
								}}><Stop /></button
							>
						{/if}
						{#if experiment.status === "paused"}
							<button
								class="icon-btn-sm green"
								onclick={async () => {
									experiment.status = "continuing";
									await continueExperiment(experiment);
								}}><Play /></button
							>
						{/if}
						{#if experiment.status === "stopping" || experiment.status === "pausing"}
							<div class="icon-btn-sm bg-slate-200">
								<div class="animate-pulse">
									<Loader />
								</div>
							</div>
						{/if}
					</div>
				</div>
			</div>
		{/each}
	</div>
</div>

{#snippet timer(time: number)}
	{@const day_object = new Date(time * 1000)}
	{@const hour = day_object.getHours() - 1}
	{@const minuet = day_object.getMinutes()}
	{@const second = day_object.getSeconds()}

	{#if hour > 0}
		{zeropad(hour)}h {zeropad(minuet)}m
	{:else if minuet > 0}
		{zeropad(minuet)}m {zeropad(second)}s
	{:else}
		{zeropad(second)}s
	{/if}
{/snippet}
