<script lang="ts" generics="T extends string | number">
	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";
	import { tick } from "svelte";
	import Label from "./Label.svelte";

	let open = $state(false);

	const clickoutside = getClickOutsideAttachment(() => {
		open = false;
	});

	let {
		label,
		mandatory = false,
		value = $bindable(),
		options,
	}: {
		label: string;
		mandatory?: boolean;
		value: T;
		options: T[];
	} = $props();
</script>

<div class="frow items-center">
	<Label {label} {mandatory} />
	<div
		{@attach clickoutside}
		class="  flex-grow w-fit border-l-1 border-slate-400 text-center relative box-border h-5">
		{#if open}
			<div
				class="bg-white absolute top-0 left-0 w-full border border-black z-1 h-fit max-h-84">
				<div class="max-h-84 overflow-y-scroll scrollbar-slate-400">
					{#each options as option}
						<button
							class={cn(
								"  w-full py-0.5 px-1",
								value === option
									? "bg-slate-700 text-white"
									: "hover:bg-slate-300"
							)}
							onclick={() => {
								value = option;
								open = false;
							}}>
							{option}
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
			class="w-full h-full py-0.5 px-1 box-border"
			onclick={() => {
				open = true;
			}}>
			{value}
		</button>
	</div>
</div>
