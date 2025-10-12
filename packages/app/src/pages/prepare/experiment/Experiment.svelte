<script lang="ts">
	import { Check, ChevronDown, ChevronRight } from "@lucide/svelte";
	import InputField from "$components/fields/InputField.svelte";

	import Label from "$components/fields/Label.svelte";
	import { EquipmentController } from "$controllers/equipment.svelte";
	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";

	import {
		experiment_controller,
		type ExperimentController,
	} from "$controllers/experiment.svelte";
	import ExperimentSelector from "./ExperimentSelector.svelte";
	import Composite from "../_ee/Composite.svelte";
	import Param from "../_ee/Param.svelte";

	let open = $state(false);

	const clickoutside = getClickOutsideAttachment(() => {
		open = false;
	});
</script>

<div class=" fcol-2 min-h-0 h-full bg-slate-200 rounded p-2">
	<div class="title">Experiment</div>

	<ExperimentSelector />

	{#if experiment_controller.status !== "undefined"}
		<div>
			<div
				class={cn(
					"grid grid-cols-2 border-2 border-slate-800 bg-slate-300 rounded-t p-0.5",
					experiment_controller.param_opens ? "" : "rounded-b"
				)}>
				<button
					class={cn(
						"frow items-center   pr-4 rounded-tr rounded-tl h-full"
					)}
					onclick={() => {
						experiment_controller.param_opens =
							!experiment_controller.param_opens;
					}}>
					<span class="h-3">
						{#if !experiment_controller.param_opens}
							<ChevronRight strokeWidth="3px" />
						{:else}
							<ChevronDown strokeWidth="3px" />
						{/if}
					</span>
					<div class="  wrapped px-0">Params</div>
				</button>
			</div>

			{#if experiment_controller.param_opens}
				<div
					class="fcol *:border-b-1 *:border-slate-400 border-2 border-t-0 border-slate-800">
					{#each Object.keys(experiment_controller.params) as key}
						{#if experiment_controller.params[key].type === "composite"}
							<Composite
								label={key}
								bind:open={
									experiment_controller.composite_opens[key]
								}
								bind:params={
									experiment_controller.params[key].children
								} />
						{:else}
							<Param
								label={key}
								bind:param={
									experiment_controller.params[key]
								} />
						{/if}
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>
