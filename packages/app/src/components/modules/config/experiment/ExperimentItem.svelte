<script lang="ts">
	import {
		experiment_controller,
		type Experiment,
	} from "$controllers/experiment.svelte";
	import {
		Clock,
		History,
		Loader,
		Pause,
		Play,
		Square,
	} from "@lucide/svelte";

	import BaseItem from "../_ee/BaseItem.svelte";
	import Timer from "./Timer.svelte";

	let { experiment = $bindable() }: { experiment: Experiment } = $props();
</script>

<BaseItem bind:ee={experiment} controller={experiment_controller}>
	<div class="fcol-2 border-2 border-slate-800 rounded p-1">
		<div class="grid grid-cols-3 gap-2">
			<div class="font-medium p-1 pb-0">Progress</div>

			<div class="frow-1 items-center justify-end col-span-2">
				{#if experiment.status === "initial" || experiment.status === "completed" || experiment.status === "stopped"}
					<button
						class="icon-btn-sm bg-green-500 text-white"
						onclick={() => {
							experiment_controller.start(experiment.name);
						}}><Play /></button>
				{:else if experiment.status === "started" || experiment.status === "running"}
					<button
						class="icon-btn-sm bg-red-500 text-white"
						onclick={() => {
							experiment_controller.pause(experiment.name);
						}}><Pause /></button>
				{:else if experiment.status === "paused" || experiment.status === "pausing"}
					<button
						class="icon-btn-sm bg-red-500 text-white"
						onclick={() => {
							experiment_controller.stop(experiment.name);
						}}><Square /></button>
				{/if}
				{#if experiment.status === "paused"}
					<button
						class="icon-btn-sm bg-green-500 text-white"
						onclick={() => {
							experiment_controller.continue(experiment.name);
						}}><Play /></button>
				{/if}
				{#if experiment.status === "stopping" || experiment.status === "pausing"}
					<div class="icon-btn-sm bg-slate-200">
						<div class="animate-pulse text-white">
							<Loader />
						</div>
					</div>
				{/if}
			</div>
			<div
				class="h-full w-full border-1 border-slate-600 bg-slate-200 relative rounded overflow-clip">
				<div
					class="absolute top-0 left-0 h-full rounded-l frow-1 w-full items-center">
					{#if experiment.status === "initial"}
						<div class="w-full text-center">- %</div>
					{:else if experiment.expected_loop_count === -1}
						<div class="w-full text-center">∞</div>
					{:else}
						{@const percentage =
							Math.round(
								(experiment.loop_count /
									experiment.expected_loop_count!) *
									10000
							) / 100}
						<div
							class="bg-slate-600 h-full frow items-center"
							style={`width: ${percentage}%`}>
							{#if percentage > 20}
								<div class="w-full text-right pr-1 text-white">
									{percentage} %
								</div>
							{/if}
						</div>
						{#if percentage <= 20}
							<div>{percentage} %</div>
						{/if}
					{/if}
				</div>
			</div>
			<div
				class="frow-2 items-center justify-between col-span-2 *:flex-1">
				<div
					class="border-1 border-slate-600 box-border bg-slate-200 rounded frow items-center justify-center">
					<span class="icon-btn-sm">
						<Clock />
					</span>
					<Timer time={experiment.total_time * 1000} class="px-1" />
				</div>

				<div
					class="border-1 border-slate-600 box-border bg-slate-200 rounded frow items-center justify-center">
					<span class="icon-btn-sm">
						<History />
					</span>
					<Timer time={experiment.loop_time * 1000} class="px-1" />
				</div>
				<div
					class="border-1 border-slate-600 box-border bg-slate-200 rounded flex-grow justify-center frow items-center h-full">
					{#if experiment.status === "initial"}
						- / -
					{:else if experiment.expected_loop_count === -1}
						∞
					{:else}
						{experiment.loop_count} / {experiment.expected_loop_count}
					{/if}
				</div>
			</div>
		</div>
	</div>
</BaseItem>
