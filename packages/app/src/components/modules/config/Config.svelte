<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import { ChevronsLeft } from "@lucide/svelte";
	import Cli from "./cli/Cli.svelte";
	import Dependency from "./dependency/Dependencies.svelte";
	import Equipments from "./equipment/Equipments.svelte";
	import Logger from "./logger/Logger.svelte";
	import Experiments from "./experiment/Experiments.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { equipment_controller } from "$controllers/equipment.svelte";

	type Page = "Dependency" | "Equipment" | "Experiment" | "Cli" | "Log";

	let page: Page = $state("Experiment");

	let { open = $bindable() } = $props();
</script>

<div class="flex flex-col w-128">
	<div class="frow-1">
		<button
			onclick={() => {
				open = false;
			}}
			class="icon-btn-sm bg-slate-800 rounded-none rounded-tr text-white flex items-center justify-center">
			<ChevronsLeft />
		</button>
		{@render tab("Dependency")}
		{@render tab("Equipment")}
		{@render tab("Experiment")}
		{@render tab("Cli")}
		{@render tab("Log")}
	</div>

	<div class={cn(" bg-slate-800 flex-grow min-h-0  p-2 fcol-2")}>
		{#if page === "Dependency"}
			<Dependency />
		{:else if page === "Equipment"}
			<Equipments />
		{:else if page === "Experiment"}
			<Experiments />
		{:else if page === "Cli"}
			<Cli />
		{:else if page === "Log"}
			<Logger />
		{/if}
		<!-- 
		<ExperimentList />
		<Editor /> 
	-->
	</div>
</div>

{#snippet tab(value: Page)}
	<button
		class={cn(
			"rounded-t  py-1 px-2 flex-1",
			page === value ? " bg-slate-800 text-slate-50" : " bg-slate-200  "
		)}
		onclick={() => {
			page = value;
			if (value === "Experiment") {
				experiment_controller.updateImports();
			} else if (value === "Equipment") {
				equipment_controller.updateImports();
			}
		}}>{value}</button>
{/snippet}
