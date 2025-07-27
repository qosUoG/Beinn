<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Cli from "./cli/Cli.svelte";
	import Dependency from "./dependency/Dependencies.svelte";
	import Logger from "./logger/Logger.svelte";

	type Page = "Dependency" | "Equipment" | "Experiment" | "Cli" | "Log";

	let page: Page = $state("Cli");
</script>

<div class="flex flex-col w-128">
	<div class="grid grid-cols-5 gap-1">
		{@render tab("Dependency")}
		{@render tab("Equipment")}
		{@render tab("Experiment")}
		{@render tab("Cli")}
		{@render tab("Log")}
	</div>

	<div class={cn(" bg-slate-800 flex-grow min-h-0 rounded-b p-2 fcol-2")}>
		{#if page === "Dependency"}
			<Dependency />
		{:else if page === "Cli"}
			<Cli />
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
