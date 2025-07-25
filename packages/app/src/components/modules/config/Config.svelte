<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Conc from "./conc/Conc.svelte";
	import Dependency from "./dependency/Dependency.svelte";
	import Logger from "./logger/Logger.svelte";

	type Page = "Dependency" | "Equipment" | "Experiment" | "Conc" | "Log";

	let page: Page = $state("Conc");
</script>

<div class="flex flex-col w-128">
	<div class="grid grid-cols-5 gap-1">
		{@render tab("Dependency")}
		{@render tab("Equipment")}
		{@render tab("Experiment")}
		{@render tab("Conc")}
		{@render tab("Log")}
	</div>

	<div class={cn(" bg-slate-800 flex-grow min-h-0 rounded-b p-2 fcol-2")}>
		{#if page === "Dependency"}
			<Dependency />
		{:else if page === "Conc"}
			<Conc />
		{:else if page === "Log"}
			<Logger />
		{/if}
		<!-- 
		<EquipmentList />
		<ExperimentList />
		<Editor /> 
	-->
	</div>
</div>

{#snippet tab(value: Page)}
	<button
		class={cn(
			"rounded-t  py-1 px-2",
			page === value ? " bg-slate-800 text-slate-50" : " bg-slate-200  "
		)}
		onclick={() => {
			page = value;
		}}>{value}</button>
{/snippet}
