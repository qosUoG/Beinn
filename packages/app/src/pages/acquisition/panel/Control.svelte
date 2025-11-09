<script lang="ts">
	import {
		experiment_controller,
		type Experiment,
	} from "$controllers/experiment.svelte";
	import { Loader, Pause, Play, Square } from "@lucide/svelte";

	let { experiment }: { experiment: Experiment } = $props();
</script>

{#snippet playBtn()}
	<button
		class="icon-btn-sm bg-green-500 text-white"
		onclick={() => {
			experiment.start();
		}}><Play /></button>
{/snippet}

{#snippet continueBtn()}
	<button
		class="icon-btn-sm bg-green-500 text-white"
		onclick={() => {
			experiment.continue();
		}}><Play /></button>
{/snippet}

{#snippet disabledPlayBtn()}
	<div class="icon-btn-sm bg-slate-300 text-white">
		<Play />
	</div>
{/snippet}

{#snippet pauseBtn()}
	<button
		class="icon-btn-sm bg-red-500 text-white"
		onclick={() => {
			experiment.pause();
		}}><Pause /></button>
{/snippet}

{#snippet disabledPauseBtn()}
	<div class="icon-btn-sm bg-slate-300 text-white">
		<Pause />
	</div>
{/snippet}

{#snippet stopBtn()}
	<button
		class="icon-btn-sm bg-red-500 text-white"
		onclick={() => {
			experiment.stop();
		}}><Square /></button>
{/snippet}

{#snippet disabledStopBtn()}
	<div class="icon-btn-sm bg-slate-300 text-white">
		<Square />
	</div>
{/snippet}

{#snippet spinner()}
	<div class="icon-btn-sm bg-slate-200">
		<div class="animate-pulse text-white">
			<Loader />
		</div>
	</div>
{/snippet}

{#snippet ready()}
	{#if experiment_controller.playable}
		{@render playBtn()}
	{:else}
		{@render disabledPlayBtn()}
	{/if}
	{@render disabledPauseBtn()}
	{@render disabledStopBtn()}
{/snippet}

{#snippet starting_looping()}
	{@render disabledPlayBtn()}
	{@render pauseBtn()}
	{@render stopBtn()}
{/snippet}

{#snippet pausing()}
	{@render continueBtn()}
	{@render spinner()}
	{@render stopBtn()}
{/snippet}

{#snippet paused()}
	{@render continueBtn()}
	{@render disabledPauseBtn()}
	{@render stopBtn()}
{/snippet}

{#snippet stopping()}
	{@render disabledPlayBtn()}
	{@render disabledPauseBtn()}
	{@render spinner()}
{/snippet}

{#snippet ended()}
	{#if experiment_controller.playable}
		{@render playBtn()}
	{:else}
		{@render disabledPlayBtn()}
	{/if}
	{@render disabledPauseBtn()}
	{@render disabledStopBtn()}
{/snippet}

<div class="frow-1 items-center">
	{#if experiment.state === "ready"}
		{@render ready()}
	{:else if experiment.state === "starting" || experiment.state === "looping"}
		{@render starting_looping()}
	{:else if experiment.state === "pausing"}
		{@render pausing()}
	{:else if experiment.state === "paused"}
		{@render paused()}
	{:else if experiment.state === "stopping"}
		{@render stopping()}
	{:else if experiment.state === "ended"}
		{@render ended()}
	{/if}
</div>
