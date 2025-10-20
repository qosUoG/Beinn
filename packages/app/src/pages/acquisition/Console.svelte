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

{#if experiment_controller.experiment}
	<div class="bg-white rounded w-128">
		<div class="fcol-2 border-2 border-slate-800 rounded p-1">
			<div class="grid grid-cols-4 gap-2">
				<div class="frow-1 items-center">
					{#if experiment_controller.experiment.state === "paused"}
						<button
							class="icon-btn-sm bg-green-500 text-white"
							onclick={() => {
								experiment_controller.experiment!.continue();
							}}><Play /></button>
					{/if}
					{#if experiment_controller.experiment.state === "ready"}
						{#if Object.values(experiment_controller.experiment.params).every( (param) => {
								if (param.type === "composite") return Object.values(param.children).every((child) => child.type !== "instance.equipment" || (child.required && child.value) || child.required === false);

								return param.type !== "instance.equipment" || (param.required && param.value) || param.required === false;
							} )}
							<button
								class="icon-btn-sm bg-green-500 text-white"
								onclick={() => {
									experiment_controller.experiment!.start();
								}}><Play /></button>
						{:else}
							<div class="icon-btn-sm bg-slate-300 text-white">
								<Play />
							</div>
						{/if}
					{:else if experiment_controller.experiment.state === "starting" || experiment_controller.experiment.state === "looping"}
						<button
							class="icon-btn-sm bg-red-500 text-white"
							onclick={() => {
								experiment_controller.experiment!.pause();
							}}><Pause /></button>
					{:else if experiment_controller.experiment.state === "paused" || experiment_controller.experiment.state === "pausing"}
						<button
							class="icon-btn-sm bg-red-500 text-white"
							onclick={() => {
								experiment_controller.experiment!.stop();
							}}><Square /></button>
					{/if}

					{#if experiment_controller.experiment.state === "stopping" || experiment_controller.experiment.state === "pausing"}
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
						{#if experiment_controller.experiment.state === "ready"}
							<div class="w-full text-center">- %</div>
						{:else if experiment_controller.experiment.expected_loop_count === -1}
							<div class="w-full text-center">∞</div>
						{:else}
							{@const percentage =
								experiment_controller.experiment
									.expected_loop_count > 0
									? Math.round(
											(experiment_controller.experiment
												.loop_count /
												experiment_controller.experiment
													.expected_loop_count!) *
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
						{#if experiment_controller.experiment.expected_loop_count > 0 && experiment_controller.experiment.loop_count > 0}
							{#key experiment_controller.experiment.total_time_clock.milliseconds - experiment_controller.experiment.loop_time_clock.milliseconds}
								<Timer
									time={((experiment_controller.experiment
										.total_time_clock.milliseconds -
										experiment_controller.experiment
											.loop_time_clock.milliseconds) /
										experiment_controller.experiment
											.loop_count) *
										(experiment_controller.experiment
											.expected_loop_count -
											experiment_controller.experiment
												.loop_count)}
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
						{#key experiment_controller.experiment.total_time_clock.milliseconds}
							<Timer
								time={experiment_controller.experiment
									.total_time_clock.milliseconds}
								class="px-1" />
						{/key}
					</div>

					<div
						class="border-1 border-slate-600 box-border bg-slate-200 rounded frow items-center justify-center">
						<span class="icon-btn-sm">
							<TimerReset />
						</span>
						{#key experiment_controller.experiment.loop_time_clock.milliseconds}
							<Timer
								time={experiment_controller.experiment
									.loop_time_clock.milliseconds}
								class="px-1" />
						{/key}
					</div>
					<div
						class="border-1 border-slate-600 box-border bg-slate-200 rounded flex-grow justify-center frow items-center h-full">
						{#if experiment_controller.experiment.state === "ready"}
							- / -
						{:else if experiment_controller.experiment.expected_loop_count === -1}
							∞
						{:else}
							{experiment_controller.experiment.loop_count} / {experiment_controller
								.experiment.expected_loop_count}
						{/if}
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}
