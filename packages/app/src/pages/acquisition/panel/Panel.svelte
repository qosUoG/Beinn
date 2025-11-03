<script lang="ts">
	import {
		Experiment,
		experiment_controller,
	} from "$controllers/experiment.svelte";

	import Control from "./Control.svelte";
	import Progress from "./Progress.svelte";
	import Remaining from "./timers/Remaining.svelte";
	import TotalTime from "./timers/TotalTime.svelte";
	import LoopTime from "./timers/LoopTime.svelte";

	let { experiment = $bindable() }: { experiment: Experiment } = $props();
</script>

<div class="bg-white rounded w-lg min-w-lg">
	<div class="fcol-2 border-2 border-slate-800 rounded p-1">
		<div class="grid grid-cols-4 gap-2">
			<Control {experiment} />
			<Progress {experiment} />
			<div class="grid grid-cols-4 gap-2 justify-between col-span-4">
				<Remaining {experiment} />

				<TotalTime {experiment} />

				<LoopTime {experiment} />

				<div
					class="border border-slate-600 box-border bg-slate-200 rounded grow justify-center frow items-center h-full">
					{#if experiment.state === "ready" && experiment.process === undefined}
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
</div>
