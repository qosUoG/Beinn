<script lang="ts">
	import { clickoutside, cn } from "$components/utils.svelte";

	let {
		options,
		value = $bindable(),
	}: {
		options: number[] | string[];
		value: number | string;
	} = $props();

	let open = $state(false);
</script>

<button
	class="min-w-0 overflow-x-scroll text-nowrap"
	onclick={(e) => {
		e.stopPropagation();
		open = !open;
		console.log({ open });
	}}>
	{value}
</button>

{#if open}
	<div
		use:clickoutside
		onoutsideclick={() => {
			open = false;
		}}
		class="absolute left-0 top-6 bg-white col-1 w-fit z-10 shadow-xl rounded">
		{#each options as option}
			<button
				class={cn(
					" wrapped  text-nowrap",
					value === option
						? "bg-slate-400 text-slate-50"
						: "hover:bg-slate-200"
				)}
				onclick={() => {
					value = option;
					open = false;
					console.log({ open });
				}}>{option}</button>
		{/each}
	</div>
{/if}
