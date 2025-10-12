<script lang="ts">
	import { equipment_controller } from "$controllers/equipment.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import EquipmentItem from "./EquipmentItem.svelte";
	import NewEquipment from "./NewEquipment.svelte";
</script>

<div class="justify-between fcol-2 min-h-0 h-full bg-slate-200 rounded p-2">
	<div class="fcol-2">
		<div class="title">Equipment</div>
		<div
			class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2 flex-grow pb-8">
			{#each equipment_controller.equipment_instances as equipment}
				<EquipmentItem bind:equipment deletable={true} />
			{/each}
		</div>
	</div>
	<NewEquipment />
</div>
