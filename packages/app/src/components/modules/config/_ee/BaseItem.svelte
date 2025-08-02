<script lang="ts">
	import {
		EquipmentController,
		type Equipment,
	} from "$controllers/equipment.svelte";

	import {
		Check,
		ChevronDown,
		ChevronRight,
		Trash2,
		Undo,
	} from "@lucide/svelte";
	import Param from "../_ee/Param.svelte";
	import Composite from "../_ee/Composite.svelte";
	import type {
		Experiment,
		ExperimentController,
	} from "$controllers/experiment.svelte";
	import type { Snippet } from "svelte";

	let {
		ee = $bindable(),
		controller,
		children,
	}:
		| { ee: Equipment; controller: EquipmentController; children?: Snippet }
		| {
				ee: Experiment;
				controller: ExperimentController;
				children?: Snippet;
		  } = $props();
</script>

<div class="bg-slate-50 rounded p-1 flex flex-col gap-0.5">
	<div class="flex items-center w-full justify-between">
		<div class="frow-2">
			<button
				aria-label="Remove dependency"
				class="bg-red-600 icon-btn-sm text-white"
				onclick={() => {
					controller.remove(ee.name);
				}}>
				<Trash2 />
			</button>
			<button
				class="frow items-center"
				onclick={() => {
					ee.param_opens = !ee.param_opens;
				}}>
				<span class="h-3">
					{#if !ee.param_opens}
						<ChevronRight strokeWidth="3px" />
					{:else}
						<ChevronDown strokeWidth="3px" />
					{/if}
				</span>
				<div class=" text-slate-950 font-medium wrapped px-0">
					{ee.name}
				</div>
			</button>
		</div>

		{#if JSON.stringify(ee.params) !== JSON.stringify(ee.temp_params)}
			<div class="frow-2">
				<button
					aria-label="Save params"
					class="bg-slate-600 icon-btn-sm text-white"
					onclick={() => {
						ee.temp_params = ee.params;
					}}>
					<Undo />
				</button>

				<button
					aria-label="Save params"
					class="bg-green-600 icon-btn-sm text-white"
					onclick={() => {
						controller.param(ee.name);
					}}>
					<Check />
				</button>
			</div>
		{/if}
	</div>
	{#if ee.param_opens}
		<div
			class="fcol *:border-1 *:border-slate-400 *:border-b-0 last:border-b-1 last:border-b-slate-400">
			{#each Object.keys(ee.temp_params) as key}
				{#if ee.temp_params[key].type === "composite"}
					<Composite
						label={key}
						bind:open={ee.composite_opens[key]}
						bind:params={ee.temp_params[key].children} />
				{:else}
					<Param label={key} bind:param={ee.temp_params[key]} />
				{/if}
			{/each}
		</div>
	{/if}
	{@render children?.()}
</div>
