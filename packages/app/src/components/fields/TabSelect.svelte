<script lang="ts" generics="T=string | number | boolean">
	import { cn } from "$components/utils.svelte";
	import Label from "./Label.svelte";

	let {
		label,
		value = $bindable(),
		items,
		mandatory = false,
	}: {
		label: string;
		value: T;
		items: { key: string; value: T }[];
		mandatory?: boolean;
	} = $props();
</script>

<div class="frow items-stretch">
	<Label {label} {mandatory} />
	<div
		class="grid flex-grow *:border-l *:border-slate-400"
		style={`grid-template-columns: repeat(${items.length}, 1fr)`}>
		{#each items as item}
			<button
				class={cn(
					"   py-0.5",
					value === item.value ? "bg-slate-300 font-semibold " : ""
				)}
				onclick={() => {
					value = item.value;
				}}>{item.key}</button
			>{/each}
	</div>
</div>
