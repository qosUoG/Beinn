<script lang="ts">
	import { equipment_controller } from "$controllers/EquipmentController.svelte";
	import { workspace_controller } from "$controllers/WorkspaceController.svelte";
	import EquipmentItem from "./EquipmentItem.svelte";
	import NewEquipment from "./NewEquipment.svelte";
</script>

{#if workspace_controller.connected}
	<div class="justify-between fcol-2 min-h-0 h-full">
		<div
			class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2 flex-grow pb-8">
			{#each equipment_controller.instances as equipment}
				<EquipmentItem bind:equipment />
			{/each}
		</div>
		<NewEquipment />
	</div>
{/if}
