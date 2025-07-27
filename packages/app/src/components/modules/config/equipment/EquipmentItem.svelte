<script lang="ts">
	import {
		equipment_controller,
		type Equipment,
	} from "$controllers/EquipmentController.svelte";
	import { Trash2 } from "@lucide/svelte";

	let { equipment }: { equipment: Equipment } = $props();
</script>

<div class="bg-slate-100 rounded p-1 flex flex-col gap-0.5">
	<div class="flex items-center w-full justify-between">
		<div class=" text-slate-950 font-medium wrapped px-0">
			{equipment.name}
		</div>
		<div class="self-stretch">
			<button
				aria-label="Remove dependency"
				class="bg-red-600 h-full aspect-square rounded flex items-center justify-center hover:bg-red-700 transition-colors -translate-x-1/2"
				onclick={() => {
					equipment_controller.remove(equipment.name);
				}}>
				<Trash2 />
			</button>
		</div>
	</div>
</div>
