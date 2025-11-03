<script lang="ts">
	import { type Experiment } from "$controllers/experiment.svelte";

	let { experiment }: { experiment: Experiment } = $props();

	let percentage = $derived.by(() => {
		if (experiment.expected_loop_count <= 0) return undefined;
		return (
			Math.round(
				(experiment.loop_count / experiment.expected_loop_count!) *
					10000
			) / 100
		);
	});
</script>

<div
	class="h-full w-full border border-slate-600 bg-slate-200 relative rounded overflow-clip col-span-3">
	<div
		class="absolute top-0 left-0 h-full rounded-l frow-1 w-full items-center">
		{#if experiment.state === "ready" && experiment.process === undefined}
			{console.log(experiment.process)}
			<div class="w-full text-center">-</div>
		{:else if experiment.expected_loop_count === -1}
			<div class="w-full text-center">∞</div>
		{:else if percentage}
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
