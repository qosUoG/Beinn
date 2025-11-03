<script lang="ts">
	import type { Experiment } from "$controllers/experiment.svelte";

	let { experiment }: { experiment: Experiment } = $props();
	import { TimerReset } from "@lucide/svelte";
	import Timer from "./Timer.svelte";
</script>

<div
	class="border border-slate-600 box-border bg-slate-200 rounded frow items-center justify-center">
	<span class="icon-btn-sm">
		<TimerReset />
	</span>
	{#key experiment.loop_time_clock.milliseconds}
		<Timer time={experiment.loop_time_clock.milliseconds} class="px-1" />
	{/key}
</div>
