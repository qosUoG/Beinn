<script lang="ts">
	import { clickoutside, cn } from "$components/utils.svelte";
	import { getRandomId } from "$lib/utils";
	import { tick } from "svelte";

	let {
		options,
		value = $bindable(),
	}: {
		options: number[] | string[];
		value: number | string;
	} = $props();

	let open = $state(false);

	const id = getRandomId([]);
</script>

<button
	class="min-w-0 overflow-x-scroll text-nowrap w-full h-full"
	onclick={async (e) => {
		open = !open;
	}}
	{id}>
	{value}
</button>

{#if open}
	<div
		use:clickoutside={id}
		onoutsideclick={() => {
			open = false;
		}}
		class="absolute left-0 top-6 bg-white col z-10 shadow-xl rounded min-w-full">
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
				}}>{option}</button>
		{/each}
	</div>
{/if}
