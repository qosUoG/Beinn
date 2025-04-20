<script lang="ts">
	import Loader from "$icons/Loader.svelte";
	import Pause from "$icons/Pause.svelte";
	import Play from "$icons/Play.svelte";
	import Rotate from "$icons/Rotate.svelte";
	import Stop from "$icons/Stop.svelte";
	import StopWatch from "$icons/StopWatch.svelte";
	import type { Experiment } from "$states/experiment.svelte";
	import Progress from "./Progress.svelte";
	import { zeropad } from "$lib/utils";

	let { experiment = $bindable() }: { experiment: Experiment } = $props();

	const startHandler = async () => {
		await experiment.start();
	};

	const pauseHandler = async () => {
		await experiment.pause();
	};

	const stopHandler = async () => {
		await experiment.stop();
	};

	const continueHandler = async () => {
		await experiment.continue();
	};

	let total_time = $state(0);
	let iteration_time = $state(0);

	setInterval(() => {
		if (
			experiment.status !== "initial" &&
			experiment.status !== "completed" &&
			experiment.status !== "paused" &&
			experiment.status !== "stopped" &&
			experiment.status !== "stopping"
		) {
			total_time = Date.now() - experiment.total_time_start;
			iteration_time = Date.now() - experiment.iteration_time_start;
		}
	}, 1000);
</script>

<div class="section bg-white fcol-2 justify-between w-full">
	<div class="grid grid-cols-2">
		<div class="wrapped bg-slate-200 w-fit">
			{experiment.name}
		</div>
		<Progress {experiment} />
	</div>

	<div class="frow justify-between">
		<div class="frow-1">
			<div class="bg-slate-200 frow rounded items-center w-24">
				<div class="icon-btn-sm">
					<StopWatch />
				</div>
				<div class="p-1 rounded pr-2 flex-grow text-center">
					{#if total_time >= 0 && experiment.status !== "initial"}
						{@render timer(total_time)}
					{:else}
						-
					{/if}
				</div>
			</div>
			<div class="bg-slate-200 frow rounded items-center w-24">
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
				{#if experiment.status === "initial"}
					- / -
				{:else}
					{experiment.iteration_count + 1}

					/ {#if experiment.proposed_total_iterations === undefined}
						∞
					{:else}
						{experiment.proposed_total_iterations}
					{/if}
				{/if}
			</div>
		</div>
		<div class="frow-1">
			{#if experiment.status === "initial" || experiment.status === "completed" || experiment.status === "stopped"}
				<button class="icon-btn-sm green" onclick={startHandler}
					><Play /></button>
			{:else if experiment.status === "continuing" || experiment.status === "started" || experiment.status === "starting" || experiment.status === "continued"}
				<button class="icon-btn-sm red" onclick={pauseHandler}
					><Pause /></button>
			{:else if experiment.status === "paused" || experiment.status === "pausing"}
				<button class="icon-btn-sm red" onclick={stopHandler}
					><Stop /></button>
			{/if}
			{#if experiment.status === "paused"}
				<button class="icon-btn-sm green" onclick={continueHandler}
					><Play /></button>
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

{#snippet timer(time: number)}
	{@const day_object = new Date(time)}
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
