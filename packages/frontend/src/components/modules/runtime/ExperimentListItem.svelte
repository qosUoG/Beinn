<script lang="ts">
	import Loader from "$icons/Loader.svelte";
	import Pause from "$icons/Pause.svelte";
	import Play from "$icons/Play.svelte";
	import Rotate from "$icons/Rotate.svelte";
	import Stop from "$icons/Stop.svelte";
	import StopWatch from "$icons/StopWatch.svelte";
	import type { Experiment } from "$states/experiment.svelte";
	import { tick } from "svelte";
	import Progress from "./Progress.svelte";
	import {
		qoslabappContinueExperiment,
		qoslabappPauseExperiment,
		qoslabappStartExperiment,
		qoslabappStopExperiment,
	} from "$services/qoslabapp.svelte";
	import { toastError } from "../ToastController.svelte";
	import type { Err } from "qoslab-shared";

	let { experiment = $bindable() }: { experiment: Experiment } = $props();

	let iteration_time = $derived(
		experiment.total_time - experiment.iteration_time_start
	);

	function zeropad(num: number) {
		if (num < 10) return `0${num}`;
		return `${num}`;
	}

	const startHandler = async () => {
		try {
			await experiment.start();
		} catch (e) {
			toastError(e as Err);
		}
	};

	const pauseHandler = async () => {
		try {
			await experiment.pause();
		} catch (e) {
			toastError(e as Err);
		}
	};

	const stopHandler = async () => {
		try {
			await experiment.stop();
		} catch (e) {
			toastError(e as Err);
		}
	};

	const continueHandler = async () => {
		try {
			await experiment.continue();
		} catch (e) {
			toastError(e as Err);
		}
	};
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
					{#if experiment.total_time >= 0 && experiment.status !== "initial"}
						{@render timer(experiment.total_time)}
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
