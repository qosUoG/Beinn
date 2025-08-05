<script lang="ts">
	import {
		equipment_controller,
		type Equipment,
	} from "$controllers/equipment.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";

	import BaseItem from "../_ee/BaseItem.svelte";

	let { equipment = $bindable() }: { equipment: Equipment } = $props();

	let deletable = $derived.by(() => {
		for (const instance of experiment_controller.instances_arr) {
			for (const param of Object.values(instance.params)) {
				if (
					param.type === "instance.equipment" &&
					param.name === equipment.name
				)
					return false;
			}
		}

		return true;
	});
</script>

<BaseItem
	bind:ee={equipment}
	controller={equipment_controller}
	bind:deletable />
