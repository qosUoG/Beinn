<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import { analysis_controller } from "$controllers/analysis.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import { X, Plus } from "@lucide/svelte";
	import { onDestroy, onMount } from "svelte";
	import Viewer from "./Viewer.svelte";
	import Finder from "./Finder.svelte";
	import Params from "./Params.svelte";
	import { app_controller } from "$controllers/app.svelte";

	onMount(() => {
		analysis_controller.load();
	});
</script>

<div class="grow p-2 pt-0 min-h-0">
	{#if workspace_controller.status === "ready"}
		<div class=" h-full frow-2 min-h-0">
			<div class="grid grid-rows-2 gap-2 min-h-0 h-full">
				<Finder />
				<div class="bg-slate-200 rounded p-1 min-h-0 h-full fcol-1">
					{#if analysis_controller.active_tab}
						<Params bind:tab={analysis_controller.active_tab} />
					{/if}
				</div>
			</div>
			<div class="h-full grow rounded fcol">
				<div class="h-6 frow gap-0.5">
					{#each analysis_controller.tabs as tab, i}
						<div
							class={cn(
								" rounded-t  px-2 border-b-2 box-border pr-6 relative h-full frow items-center",
								i === analysis_controller.active_tab_index
									? "border-slate-200 bg-slate-200"
									: "border-white bg-slate-200/60 "
							)}>
							<button
								class={cn(
									"frow items-center h-full ",
									tab === undefined ? "italic " : ""
								)}
								onclick={() => {
									analysis_controller.active_tab_index = i;
								}}>
								{#if tab}
									{tab.key}
								{:else}
									New Tab
								{/if}
							</button>
							<button
								class="absolute h-4 w-4 p-0.5 right-1 top-1/2 -translate-y-1/2"
								onclick={() => {
									analysis_controller.removeTab(i);
								}}>
								<X />
							</button>
						</div>
					{/each}

					<button
						class="icon-btn-sm rounded-b-none bg-slate-200 border-b-2 border-white box-border"
						onclick={() => {
							analysis_controller.addTab();
						}}>
						<Plus />
					</button>
				</div>
				<div class="bg-slate-200 grow rounded-b p-2 fcol-2">
					{#if analysis_controller.active_tab}
						<Viewer bind:tab={analysis_controller.active_tab} />
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>
