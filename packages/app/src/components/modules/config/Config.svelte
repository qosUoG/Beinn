<script lang="ts">
	import Editor from "$components/modules/config/editor/Editor.svelte";
	import EquipmentList from "$components/modules/config/list/EquipmentList.svelte";
	import ExperimentList from "$components/modules/config/list/ExperimentList.svelte";
	import DependencyList from "$components/modules/config/list/DependencyList.svelte";
	import { cn } from "$components/utils.svelte";
	import DependencyItem from "./DependencyItem.svelte";
	import { workspace } from "$states/workspace.svelte";
	import { controller } from "../../../controllers/app_controller.svelte";
	import NewDependency from "./NewDependency.svelte";
	import Separator from "$components/reuseables/Separator.svelte";
	type Page = "Dependency" | "Equipment" | "Experiment" | "CLI" | "Log";

	let page: Page = $state("Dependency");
</script>

<div class="flex flex-col">
	<div class="grid grid-cols-5 gap-1">
		{@render tab("Dependency")}
		{@render tab("Equipment")}
		{@render tab("Experiment")}
		{@render tab("CLI")}
		{@render tab("Log")}
	</div>

	<div class={cn(" bg-slate-800 flex-grow min-h-0 rounded-b p-2 fcol-2")}>
		{#if page === "Dependency"}
			{#if controller.connected}
				<div class="justify-between fcol-2 min-h-0 h-full">
					<div
						class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2">
						{#each controller.dependencies as dependency}
							<DependencyItem {dependency} />
						{/each}
					</div>

					<NewDependency />
				</div>
			{/if}
		{:else if page === "Log"}
			<div></div>
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
