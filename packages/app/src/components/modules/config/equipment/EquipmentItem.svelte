<script lang="ts">
	import {
		equipment_controller,
		type Equipment,
	} from "$controllers/equipment.svelte";

	import BaseItem from "../_ee/BaseItem.svelte";

	let { equipment = $bindable() }: { equipment: Equipment } = $props();
</script>

<BaseItem bind:ee={equipment} controller={equipment_controller} />
