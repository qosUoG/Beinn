<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import {
		CalendarClock,
		Clock,
		Loader,
		Pause,
		Play,
		Square,
		TimerReset,
	} from "@lucide/svelte";
	import Timer from "./Timer.svelte";
</script>

<div class="fcol-2 border-2 border-slate-800 rounded p-1">
	<div class="grid grid-cols-4 gap-2">
		<div class="frow-1 items-center">
			{#if experiment_controller.status === "paused"}
				<button
					class="icon-btn-sm bg-green-500 text-white"
					onclick={() => {
						experiment_controller.continue();
					}}><Play /></button>
			{/if}
			{#if experiment_controller.status === "initial" || experiment_controller.status === "completed" || experiment_controller.status === "stopped"}
				{#if Object.values(experiment_controller.params).every( (param) => {
						if (param.type === "composite") return Object.values(param.children).every((child) => child.type !== "instance.equipment" || (child.required && child.name) || child.required === false);

						return param.type !== "instance.equipment" || (param.required && param.name) || param.required === false;
					} )}
					<button
						class="icon-btn-sm bg-green-500 text-white"
						onclick={() => {
							experiment_controller.start();
						}}><Play /></button>
				{:else}
					<div class="icon-btn-sm bg-slate-300 text-white">
						<Play />
					</div>
				{/if}
			{:else if experiment_controller.status === "started" || experiment_controller.status === "running"}
				<button
					class="icon-btn-sm bg-red-500 text-white"
					onclick={() => {
						experiment_controller.pause();
					}}><Pause /></button>
			{:else if experiment_controller.status === "paused" || experiment_controller.status === "pausing"}
				<button
					class="icon-btn-sm bg-red-500 text-white"
					onclick={() => {
						experiment_controller.stop();
					}}><Square /></button>
			{/if}

			{#if experiment_controller.status === "stopping" || experiment_controller.status === "pausing"}
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
				{#if experiment_controller.status === "initial"}
					<div class="w-full text-center">- %</div>
				{:else if experiment_controller.expected_loop_count === -1}
					<div class="w-full text-center">∞</div>
				{:else}
					{@const percentage =
						experiment_controller.expected_loop_count > 0
							? Math.round(
									(experiment_controller.loop_count /
										experiment_controller.expected_loop_count!) *
										10000
								) / 100
							: 0}
					<div
						class="bg-slate-600 h-full frow items-center"
						style={`width: ${percentage}%`}>
						{#if percentage > 40}
							<div class="w-full text-right pr-1.5 text-white">
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
				{#if experiment_controller.expected_loop_count > 0 && experiment_controller.loop_count > 0}
					{#key experiment_controller.total_time - experiment_controller.loop_time}
						<Timer
							time={((experiment_controller.total_time -
								experiment_controller.loop_time) /
								experiment_controller.loop_count) *
								(experiment_controller.expected_loop_count -
									experiment_controller.loop_count)}
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
				{#key experiment_controller.total_time}
					<Timer
						time={experiment_controller.total_time}
						class="px-1" />
				{/key}
			</div>

			<div
				class="border-1 border-slate-600 box-border bg-slate-200 rounded frow items-center justify-center">
				<span class="icon-btn-sm">
					<TimerReset />
				</span>
				{#key experiment_controller.loop_time}
					<Timer
						time={experiment_controller.loop_time}
						class="px-1" />
				{/key}
			</div>
			<div
				class="border-1 border-slate-600 box-border bg-slate-200 rounded flex-grow justify-center frow items-center h-full">
				{#if experiment_controller.status === "initial"}
					- / -
				{:else if experiment_controller.expected_loop_count === -1}
					∞
				{:else}
					{experiment_controller.loop_count} / {experiment_controller.expected_loop_count}
				{/if}
			</div>
		</div>
	</div>
</div>
