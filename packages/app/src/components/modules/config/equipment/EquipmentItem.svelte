<script lang="ts">
	import DropSelect from "$components/fields/DropSelect.svelte";
	import InputField from "$components/fields/InputField.svelte";
	import TabSelect from "$components/fields/TabSelect.svelte";
	import { autofocus } from "$components/utils.svelte";
	import {
		equipment_controller,
		type Equipment,
	} from "$controllers/EquipmentController.svelte";

	import { Trash2 } from "@lucide/svelte";
	import Param from "../Param.svelte";
	import Composite from "../Composite.svelte";

	let { equipment = $bindable() }: { equipment: Equipment } = $props();
</script>

<div class="bg-slate-50 rounded p-1 flex flex-col gap-0.5">
	<div class="flex items-center w-full justify-between">
		<div class=" text-slate-950 font-medium wrapped px-0">
			{equipment.name}
		</div>
		<div class="self-stretch">
			<button
				aria-label="Remove dependency"
				class="bg-red-600 icon-btn-sm text-white"
				onclick={() => {
					equipment_controller.remove(equipment.name);
				}}>
				<Trash2 />
			</button>
		</div>
	</div>

	<div
		class="fcol *:border-1 *:border-slate-400 *:border-b-0 last:border-b-1 last:border-b-slate-400">
		{#each Object.keys(equipment.temp_params) as key}
			{#if equipment.temp_params[key].type === "composite"}
				<Composite
					label={key}
					bind:params={equipment.temp_params[key].children} />
			{:else}
				<Param label={key} bind:param={equipment.temp_params[key]} />
			{/if}
		{/each}
	</div>
</div>
