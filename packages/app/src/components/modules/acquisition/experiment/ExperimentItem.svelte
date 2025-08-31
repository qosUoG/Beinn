<script lang="ts">
	import {
		experiment_controller,
		type Experiment,
	} from "$controllers/experiment.svelte";
	import {
		CalendarClock,
		Clock,
		Loader,
		Pause,
		Play,
		Square,
		TimerReset,
	} from "@lucide/svelte";

	import BaseItem from "../_ee/BaseItem.svelte";
	import Timer from "./Timer.svelte";

	let { experiment = $bindable() }: { experiment: Experiment } = $props();
</script>

<BaseItem
	bind:ee={experiment}
	controller={experiment_controller}
	deletable={!experiment.status.endsWith("ing")}>
	<div class="fcol-2 border-2 border-slate-800 rounded p-1">
		<div class="grid grid-cols-4 gap-2">
			<div class="frow-1 items-center">
				{#if experiment.status === "paused"}
					<button
						class="icon-btn-sm bg-green-500 text-white"
						onclick={() => {
							experiment_controller.continue(experiment.name);
						}}><Play /></button>
				{/if}
				{#if experiment.status === "initial" || experiment.status === "completed" || experiment.status === "stopped"}
					{#if JSON.stringify(experiment.params) === JSON.stringify(experiment.temp_params) && Object.values(experiment.params).every( (param) => {
								if (param.type === "composite") return Object.values(param.children).every((child) => child.type !== "instance.equipment" || (child.required && child.name) || child.required === false);

								return param.type !== "instance.equipment" || (param.required && param.name) || param.required === false;
							} )}
						<button
							class="icon-btn-sm bg-green-500 text-white"
							onclick={() => {
								experiment_controller.start(experiment.name);
							}}><Play /></button>
					{:else}
						<div class="icon-btn-sm bg-slate-300 text-white">
							<Play />
						</div>
					{/if}
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

				{#if experiment.status === "stopping" || experiment.status === "pausing"}
					<div class="icon-btn-sm bg-slate-200">
						<div class="animate-pulse text-white">
							<Loader />
						</div>
					</div>
				{/if}
			</div>
			<div
				class="h-full w-full border-1 border-slate-600 bg-slate-200 relative rounded overflow-clip col-span-3">
				<div
					class="absolute top-0 left-0 h-full rounded-l frow-1 w-full items-center">
					{#if experiment.status === "initial"}
						<div class="w-full text-center">- %</div>
					{:else if experiment.expected_loop_count === -1}
						<div class="w-full text-center">∞</div>
					{:else}
						{@const percentage =
							experiment.expected_loop_count > 0
								? Math.round(
										(experiment.loop_count /
											experiment.expected_loop_count!) *
											10000
									) / 100
								: 0}
						<div
							class="bg-slate-600 h-full frow items-center"
							style={`width: ${percentage}%`}>
							{#if percentage > 40}
								<div
									class="w-full text-right pr-1.5 text-white">
									{percentage}%
								</div>
							{/if}
						</div>
						{#if percentage <= 40}
							<div class="pl-0.5">{percentage}%</div>
						{/if}
					{/if}
				</div>
			</div>
			<div class="grid grid-cols-4 gap-2 justify-between col-span-4">
				<div
					class="border-1 border-slate-600 box-border bg-slate-200 rounded frow items-center justify-center">
					<span class="icon-btn-sm">
						<CalendarClock />
					</span>
					{#if experiment.expected_loop_count > 0 && experiment.loop_count > 0}
						{#key experiment.total_time - experiment.loop_time}
							<Timer
								time={((experiment.total_time -
									experiment.loop_time) /
									experiment.loop_count) *
									(experiment.expected_loop_count -
										experiment.loop_count)}
								class="px-1" />
						{/key}
					{:else}
						-
					{/if}
				</div>

				<div
					class="border-1 border-slate-600 box-border bg-slate-200 rounded frow items-center justify-center">
					<span class="icon-btn-sm">
						<Clock />
					</span>
					{#key experiment.total_time}
						<Timer time={experiment.total_time} class="px-1" />
					{/key}
				</div>

				<div
					class="border-1 border-slate-600 box-border bg-slate-200 rounded frow items-center justify-center">
					<span class="icon-btn-sm">
						<TimerReset />
					</span>
					{#key experiment.loop_time}
						<Timer time={experiment.loop_time} class="px-1" />
					{/key}
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
