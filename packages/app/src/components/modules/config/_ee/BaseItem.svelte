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
	import { cn } from "$components/utils.svelte";
	import { deepCopy } from "$lib/utils";

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

<div class="bg-slate-50 rounded p-1 fcol">
	<div class="flex items-center w-full justify-between mb-1">
		<div class=" text-slate-950 font-medium">
			{ee.name}
		</div>

		<button
			aria-label="Remove dependency"
			class="bg-red-600 icon-btn-sm text-white"
			onclick={() => {
				controller.remove(ee.name);
			}}>
			<Trash2 />
		</button>
	</div>

	<div class="frow justify-between h-7">
		<button
			class={cn(
				"frow items-center bg-slate-800  w-fit pr-4 rounded-t",
				ee.param_opens ? "" : "rounded-b"
			)}
			onclick={() => {
				ee.param_opens = !ee.param_opens;
			}}>
			<span class="h-3 text-white">
				{#if !ee.param_opens}
					<ChevronRight strokeWidth="3px" />
				{:else}
					<ChevronDown strokeWidth="3px" />
				{/if}
			</span>
			<div class="  font-medium wrapped px-0 text-white">Params</div>
		</button>

		{#if JSON.stringify(ee.params) !== JSON.stringify(ee.temp_params)}
			<div class="frow-1 items-center">
				<button
					aria-label="Save params"
					class="bg-slate-600 icon-btn-sm text-white"
					onclick={() => {
						ee.temp_params = deepCopy(ee.params);
					}}>
					<Undo />
				</button>

				<button
					aria-label="Save params"
					class="bg-green-600 icon-btn-sm text-white"
					onclick={() => {
						controller.updateParams(ee.name);
					}}>
					<Check />
				</button>
			</div>
		{/if}
	</div>

	{#if ee.param_opens}
		<div
			class="fcol *:border-b-1 *:border-slate-400 border-2 border-slate-800">
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
