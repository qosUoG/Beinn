<script lang="ts">
	import { equipment_controller } from "$controllers/equipment.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import EquipmentItem from "./EquipmentItem.svelte";
	import NewEquipment from "./NewEquipment.svelte";
</script>

{#if workspace_controller.connection === "connected"}
	<div class="justify-between fcol-2 min-h-0 h-full">
		<div
			class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2 flex-grow pb-8">
			{#each equipment_controller.instances_arr as equipment}
				<EquipmentItem bind:equipment />
			{/each}
		</div>
		<NewEquipment />
	</div>
{/if}
