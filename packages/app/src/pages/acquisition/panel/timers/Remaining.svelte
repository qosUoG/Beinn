<script lang="ts">
	import { CalendarClock } from "@lucide/svelte";
	import Timer from "./Timer.svelte";
	import type { Experiment } from "$controllers/experiment.svelte";

	let { experiment }: { experiment: Experiment } = $props();

	let show_time = $derived(
		experiment.expected_loop_count > 0 && experiment.loop_count > 0
	);

	let time = $derived.by(() => {
		if (experiment.starting_time_total === undefined) return 0;

		return (
			((experiment.total_time_clock.milliseconds -
				experiment.starting_time_total -
				experiment.loop_time_clock.milliseconds) /
				experiment.loop_count) *
			(experiment.expected_loop_count - experiment.loop_count)
		);
	});
</script>

<div
	class="border border-slate-600 box-border bg-slate-200 rounded frow items-center justify-center">
	<span class="icon-btn-sm">
		<CalendarClock />
	</span>
	{#if show_time}
		{#key experiment.total_time_clock.milliseconds - experiment.loop_time_clock.milliseconds}
			<Timer {time} class="px-1" />
		{/key}
	{:else}
		-
	{/if}
</div>
