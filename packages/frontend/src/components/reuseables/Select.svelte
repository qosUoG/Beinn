<script lang="ts">
	import { clickoutside, cn } from "$components/utils.svelte";

	let {
		open = $bindable(),
		options,
		selection = $bindable(),
	}: {
		open: boolean;
		options: number[] | string[];
		selection: number;
	} = $props();
</script>

<button
	class="w-full"
	onclick={(e) => {
		e.stopPropagation();
		open = true;
	}}>{options[selection]}</button>

{#if open}
	<div
		use:clickoutside
		onoutsideclick={() => {
			open = false;
		}}
		class="absolute right-0 top-7 bg-white container col-1 w-full z-10 shadow-xl">
		{#each options as option, i}
			<button
				class={cn(
					" wrapped",
					selection === i
						? "bg-slate-400 text-slate-50"
						: "hover:bg-slate-200"
				)}
				onclick={() => {
					selection = i;
					open = false;
				}}>{option}</button>
		{/each}
	</div>
{/if}
