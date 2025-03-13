<script lang="ts" generics="T extends string | number">
	import { clickoutside, cn } from "$components/utils.svelte";
	import { getRandomId } from "$lib/utils";
	import { tick } from "svelte";

	let {
		options,
		value = $bindable(),
	}: {
		value: T;
		options: T[];
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
		{#each options as option, i}
			<button
				class={cn(
					" wrapped  text-nowrap text-left rounded-none",
					i === 0 ? "rounded-t" : "",
					i === options.length - 1 ? "rounded-b" : "",
					value === option
						? "bg-slate-500 text-slate-50"
						: "hover:bg-slate-300"
				)}
				onclick={() => {
					value = option;
					open = false;
				}}>{option}</button>
		{/each}
	</div>
{/if}
