<script lang="ts" generics="T extends string | number">
	import { clickoutside, cn } from "$components/utils.svelte";
	import { getRandomId } from "$lib/utils";

	let {
		options,

		value = $bindable(),
	}: {
		value: T;
		options: T[] | { key: string; value: T }[];
	} = $props();

	let open = $state(false);

	const id = getRandomId([]);

	let selected_key = $derived.by(() => {
		if (typeof options[0] === "string" || typeof options[0] === "number")
			return value;

		if (!value) return "";

		return (options as { key: string; value: T }[]).find(
			(option) => option.value === value,
		)!.key;
	});
</script>

<button
	class="min-w-0 overflow-x-scroll text-nowrap w-full absolute top-0 left-0 pl-2"
	onclick={async (e) => {
		open = !open;
	}}
	{id}
>
	{selected_key}
</button>

{#if open}
	<div
		use:clickoutside={id}
		onoutsideclick={() => {
			open = false;
		}}
		class="absolute left-0 top-6 bg-white fcol z-10 shadow-xl rounded min-w-full"
	>
		{#each options as option, i}
			<button
				class={cn(
					" wrapped  text-nowrap text-left rounded-none",
					i === 0 ? "rounded-t" : "",
					i === options.length - 1 ? "rounded-b" : "",
					value === option
						? "bg-slate-500 text-slate-50"
						: "hover:bg-slate-300",
				)}
				onclick={() => {
					if (
						typeof option === "string" ||
						typeof option === "number"
					)
						value = option;
					else value = option.value;

					open = false;
				}}
			>
				{#if typeof option === "string" || typeof option === "number"}
					{option}
				{:else}
					{option.key}
				{/if}
			</button>
		{/each}
	</div>
{/if}
