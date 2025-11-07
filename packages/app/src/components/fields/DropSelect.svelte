<script lang="ts" generics="T">
	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";
	import { tick } from "svelte";
	import Label from "./Label.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { deepCopy } from "$lib/utils";

	let open = $state(false);

	const clickoutside = getClickOutsideAttachment(() => {
		open = false;
	});

	let {
		label,
		mandatory = false,
		value = $bindable(),
		options,
		editable = true,
	}: {
		label: string;
		mandatory?: boolean;
		value: { key: string; value: T };
		options: { key: string; value: T }[];
		editable?: boolean;
	} = $props();
</script>

<div class="frow items-center">
	<Label {label} {mandatory} />
	<div
		class="  grow w-fit border-l border-slate-400 text-center relative box-border h-5">
		{#if open}
			<div
				{@attach clickoutside}
				class="bg-white absolute top-0 left-0 w-full border border-black z-1 h-fit max-h-84">
				<div class="max-h-84 overflow-y-scroll scrollbar-slate-400">
					{#each options as option}
						<button
							class={cn(
								"  w-full py-0.5 px-1",
								value.key === option.key &&
									value.key === option.value
									? "bg-slate-700 text-white"
									: "hover:bg-slate-300"
							)}
							onclick={() => {
								value = option;
								open = false;
							}}>
							{option.key}
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
		{#if experiment_controller.editable && editable}
			<button
				class="w-full h-full py-0.5 px-1 box-border"
				onclick={(e) => {
					open = true;
					e.stopPropagation();
				}}>
				{value.key}
			</button>
		{:else}
			<div class="w-full h-full py-0.5 px-1 box-border">
				{value.key}
			</div>
		{/if}
	</div>
</div>
