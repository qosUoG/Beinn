<script lang="ts">
	import {
		EquipmentController,
		type Equipment,
	} from "$controllers/EquipmentController.svelte";

	import { Check, Trash2, Undo } from "@lucide/svelte";
	import Param from "../_ee/Param.svelte";
	import Composite from "../_ee/Composite.svelte";
	import type {
		Experiment,
		ExperimentController,
	} from "$controllers/ExperimentController.svelte";

	let {
		ee = $bindable(),
		controller,
	}:
		| { ee: Equipment; controller: EquipmentController }
		| { ee: Experiment; controller: ExperimentController } = $props();
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
			<div class=" text-slate-950 font-medium wrapped px-0">
				{ee.name}
			</div>
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
						controller.save(ee.name);
					}}>
					<Check />
				</button>
			</div>
		{/if}
	</div>

	<div
		class="fcol *:border-1 *:border-slate-400 *:border-b-0 last:border-b-1 last:border-b-slate-400">
		{#each Object.keys(ee.temp_params) as key}
			{#if ee.temp_params[key].type === "composite"}
				<Composite
					label={key}
					bind:open={controller.composite_opens[`${ee.name}.${key}`]}
					bind:params={ee.temp_params[key].children} />
			{:else}
				<Param label={key} bind:param={ee.temp_params[key]} />
			{/if}
		{/each}
	</div>
</div>
