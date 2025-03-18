<script lang="ts">
	import type { RuntimeExperiment } from "$states/experiment";

	let { experiment }: { experiment: RuntimeExperiment } = $props();
</script>

{#if experiment.proposed_total_loop === -1}
	<div
		class="wrapped text-center bg-slate-950 text-white rounded-full w-full">
		∞
	</div>
{:else if experiment.proposed_total_loop !== undefined}
	{@const percentage =
		experiment.loop_count + 1 / experiment.proposed_total_loop!}
	{@render progress(percentage)}
{:else}
	<div class="wrapped text-center bg-slate-200 rounded-full w-full"></div>
{/if}

{#snippet progress(value: number)}
	<div class="bg-slate-400 w-full rounded-full overflow-clip relative">
		<div class="w-full flex bg-none items-center h-full">
			<div
				class=" w-fit text-center m-auto z-10 wrapped text-white font-semibold">
				{value} %
			</div>
		</div>
		<div
			class="bg-slate-950 h-full absolute left-0 top-0"
			style={`width: ${value}%`}>
		</div>
	</div>
{/snippet}
