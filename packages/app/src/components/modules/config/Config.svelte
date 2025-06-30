<script lang="ts">
	import Editor from "$components/modules/config/editor/Editor.svelte";
	import EquipmentList from "$components/modules/config/list/EquipmentList.svelte";
	import ExperimentList from "$components/modules/config/list/ExperimentList.svelte";
	import DependencyList from "$components/modules/config/list/DependencyList.svelte";
	import { cn } from "$components/utils.svelte";
	import DependencyItem from "./DependencyItem.svelte";
	import { workspace } from "$states/workspace.svelte";
	import { controller } from "../../../controllers/app_controller.svelte";
	type Page = "Dependency" | "Equipment" | "Experiment" | "CLI" | "Log";

	let page: Page = $state("Dependency");
</script>

<div class="flex flex-col">
	<div class="flex justify-between gap-1">
		{@render tab("Dependency")}
		{@render tab("Equipment")}
		{@render tab("Experiment")}
		{@render tab("CLI")}
		{@render tab("Log")}
	</div>

	<div
		class="w-84 bg-slate-800 h-full rounded-b overflow-x-scroll scrollbar-slate-400 p-2">
		{#if page === "Dependency"}
			<div class="flex flex-col gap-2">
				{#each controller.dependencies as dependency}
					<DependencyItem {dependency} />
				{/each}
			</div>
		{/if}
		<!-- 
		<EquipmentList />
		<ExperimentList />
		<Editor /> -->
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
