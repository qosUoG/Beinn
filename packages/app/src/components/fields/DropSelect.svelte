<script lang="ts" generics="T extends string | number">
	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";
	import Label from "./Label.svelte";

	let open = $state(false);

	const clickoutside = getClickOutsideAttachment(() => {
		open = false;
	});

	let {
		label,
		value = $bindable(),
		options,
	}: {
		label: string;
		value: T;
		options: { label: string; value: T }[] | T[];
	} = $props();
</script>

<div class="frow items-center">
	<Label {label} />
	<div
		{@attach clickoutside}
		class=" py-0.5 px-1 flex-grow w-fit border-l-1 border-slate-400 text-center relative">
		{#if open}
			<div class="bg-white absolute top-0 left-0 w-full rounded border">
				<div class="overflow-scroll-y">
					{#each options as option}
						<button
							class={cn(
								" wrapped w-full",
								value === option ||
									(typeof option === "object" &&
										"value" in option &&
										option.value === value)
									? "bg-slate-800 text-slate-500"
									: "hover:bg-slate-100"
							)}
							onclick={() => {
								if (typeof option !== "object") value = option;
								else value = option.value;

								open = false;
							}}>
							{label}
						</button>
					{:else}
						<button
							onclick={() => {
								open = false;
							}}
							class="text-slate-400 wrapped italic select-none cursor-default">
							No option provided
						</button>
					{/each}
				</div>
			</div>
		{/if}
		<button
			class="w-full"
			onclick={() => {
				open = true;
			}}>
			{#if typeof options[0] !== "object"}
				{value}
			{:else}
				{(options as { label: string; value: T }[]).find(
					({ value: val }) => value === val
				)?.label}
			{/if}
		</button>
	</div>
</div>
