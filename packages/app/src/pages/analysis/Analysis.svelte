<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import { analysis_controller } from "$controllers/analysis.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import { X, Plus } from "@lucide/svelte";
	import { onMount } from "svelte";
	import Viewer from "./Viewer.svelte";
	import Finder from "./Finder.svelte";
	import Params from "./Params.svelte";

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

			<div class="bg-slate-200 grow rounded p-2 fcol-2">
				{#if analysis_controller.active_tab}
					<Viewer bind:tab={analysis_controller.active_tab} />
				{/if}
			</div>
		</div>
	{/if}
</div>
