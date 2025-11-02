<script lang="ts" generics="T=string | number | boolean">
	import { cn } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import Label from "./Label.svelte";

	let {
		label,
		value = $bindable(),
		items,
		mandatory = false,
		editable = true,
	}: {
		label: string;
		value: T;
		items: { key: string; value: T }[];
		mandatory?: boolean;
		editable?: boolean;
	} = $props();
</script>

<div class="frow items-center">
	<Label {label} {mandatory} />
	<div
		class="grid grow *:border-l *:border-slate-400"
		style={`grid-template-columns: repeat(${items.length}, 1fr)`}>
		{#each items as item}
			{#if experiment_controller.editable && editable}
				<button
					class={cn(
						"   py-0.5",
						value === item.value
							? "bg-slate-700 text-white font-semibold "
							: ""
					)}
					onclick={() => {
						value = item.value;
					}}>{item.key}</button>
			{:else}
				<div
					class={cn(
						"   py-0.5 text-center",
						value === item.value
							? "bg-slate-700 text-white font-semibold "
							: ""
					)}>
					{item.key}
				</div>
			{/if}
		{/each}
	</div>
</div>
