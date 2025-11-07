<script lang="ts">
	import {
		ChevronDown,
		ChevronRight,
		FolderSync,
		LoaderCircle,
	} from "@lucide/svelte";

	import { cn } from "$components/utils.svelte";

	import { experiment_controller } from "$controllers/experiment.svelte";
	import ExperimentSelector from "./ExperimentSelector.svelte";

	import ParamList from "../_ee/ParamList.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
</script>

<div class=" fcol-2 min-h-0 bg-slate-200 rounded p-2">
	<div class="frow justify-between items-center">
		<div class="title">Experiment</div>
		{#if experiment_controller.experiment}
			{#if experiment_controller.experiment.reloading}
				<div class="icon-btn-sm bg-blue-600">
					<div class="text-white animate-spin">
						<LoaderCircle />
					</div>
				</div>
			{:else}
				<button
					aria-label={`Reload ${experiment_controller.experiment.name}`}
					class={cn(
						" icon-btn-sm text-white ",
						experiment_controller.editable
							? "bg-blue-600"
							: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
					)}
					onclick={() => {
						if (experiment_controller.editable)
							experiment_controller.experiment!.reload();
					}}>
					<FolderSync />
				</button>{/if}
		{/if}
	</div>

	{#if workspace_controller.status === "ready"}
		<ExperimentSelector />

		{#if experiment_controller.experiment}
			<div class=" overflow-y-scroll scrollbar-slate-400 -mr-2 grow pb-8">
				<div
					class={cn(
						"grid grid-cols-2 border-2 border-slate-800 bg-slate-300 rounded-t p-0.5",
						experiment_controller.experiment.param_opens
							? ""
							: "rounded-b"
					)}>
					<button
						class={cn(
							"frow items-center   pr-4 rounded-tr rounded-tl h-full"
						)}
						onclick={() => {
							experiment_controller.experiment!.param_opens =
								!experiment_controller.experiment!.param_opens;
						}}>
						<span class="h-3">
							{#if !experiment_controller.experiment.param_opens}
								<ChevronRight strokeWidth="3px" />
							{:else}
								<ChevronDown strokeWidth="3px" />
							{/if}
						</span>
						<div class="  wrapped px-0">Params</div>
					</button>
				</div>
				<div class="bg-white">
					<ParamList
						param_opens={experiment_controller.experiment
							.param_opens}
						bind:composite_opens={
							experiment_controller.experiment.composite_opens
						}
						bind:params={experiment_controller.experiment.params}
						saveFn={async () => {
							await experiment_controller.save();
						}} />
				</div>
			</div>
		{/if}
	{/if}
</div>
