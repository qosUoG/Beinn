<script lang="ts">
	import { clickoutside, cn } from "$components/utils.svelte";

	let {
		open = $bindable(),
		options,
		value = $bindable(),
	}: {
		open: boolean;
		options: number[] | string[];
		value: number | string;
	} = $props();
</script>

<button
	class="w-full"
	onclick={(e) => {
		e.stopPropagation();
		open = true;
	}}>{value}</button>

{#if open}
	<div
		use:clickoutside
		onoutsideclick={() => {
			open = false;
		}}
		class="absolute right-0 top-7 bg-white container col-1 w-full z-10 shadow-xl">
		{#each options as option}
			<button
				class={cn(
					" wrapped",
					value === option
						? "bg-slate-400 text-slate-50"
						: "hover:bg-slate-200"
				)}
				onclick={() => {
					value = option;
					open = false;
				}}>{option}</button>
		{/each}
	</div>
{/if}
