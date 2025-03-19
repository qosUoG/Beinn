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

	let runnable_experiments = $derived(
		Object.values(gstore.experiments).filter(
			(experiment) =>
				experiment.created &&
				experiment.name &&
				experiment.name.length > 0 &&
				JSON.stringify(experiment.params) ===
					JSON.stringify(experiment.temp_params) &&
				experiment.params !== undefined
		) as CreatedRuntimeExperiment[]
	);

	function zeropad(num: number) {
		if (num < 10) return `0${num}`;
		return `${num}`;
	}
</script>

<div class="col-2 w-96 section bg-slate-200">
	{#each runnable_experiments as experiment}
		{@const loop_time = experiment.total_time - experiment.loop_time_start}
		{console.log(experiment)}
		<div class="section bg-white col-2 justify-between w-full">
			<div class="grid grid-cols-2">
				<div class="wrapped bg-slate-200 w-fit">
					{experiment.name}
				</div>
				<Progress {experiment} />
			</div>

			<div class="row justify-between">
				<div class="row-1">
					<div class="bg-slate-200 row rounded items-center w-24">
						<div class="icon-btn-sm">
							<StopWatch />
						</div>
						<div class="p-1 rounded pr-2 flex-grow text-center">
							{#if experiment.total_time > 0}
								{@render timer(experiment.total_time)}
							{:else}
								-
							{/if}
						</div>
					</div>
					<div class="bg-slate-200 row rounded items-center w-24">
						<div class="icon-btn-sm">
							<Rotate />
						</div>
						<div class="p-1 rounded pr-2 flex-grow text-center">
							{#if loop_time >= 0 && experiment.status !== "initial"}
								{@render timer(loop_time)}
							{:else}
								-
							{/if}
						</div>
					</div>

					<div class="wrapped bg-slate-200 min-w-12 text-center">
						{#if experiment.loop_count + 1 < 0}
							-
						{:else}
							{experiment.loop_count + 1}
						{/if}

						/ {#if experiment.proposed_total_loop === undefined}
							-
						{:else if experiment.proposed_total_loop === -1}
							∞
						{:else}
							{experiment.proposed_total_loop}
						{/if}
					</div>
				</div>
				<div class="row-1">
					{#if experiment.status === "initial" || experiment.status === "completed"}
						<button
							class="icon-btn-sm green"
							onclick={async () => {
								await startExperiment(experiment);
							}}><Play /></button>
					{:else if experiment.status === "continuing" || experiment.status === "started" || experiment.status === "starting" || experiment.status === "continued"}
						<button
							class="icon-btn-sm red"
							onclick={async () => {
								await pauseExperiment(experiment);
							}}><Pause /></button>
					{:else if experiment.status === "paused" || experiment.status === "pausing"}
						<button
							class="icon-btn-sm red"
							onclick={async () => {
								await stopExperiment(experiment);
							}}><Stop /></button>
					{/if}
					{#if experiment.status === "paused"}
						<button
							class="icon-btn-sm red"
							onclick={async () => {
								await continueExperiment(experiment);
							}}><Play /></button>
					{/if}
				</div>
			</div>
		</div>
	{/each}
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
