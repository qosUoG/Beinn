<script lang="ts">
	import {
		experiment_controller,
		type Experiment,
	} from "$controllers/experiment.svelte";

	import BaseItem from "../_ee/BaseItem.svelte";

	let { experiment = $bindable() }: { experiment: Experiment } = $props();
</script>

<BaseItem bind:ee={experiment} controller={experiment_controller}>
	<div>hi</div>
</BaseItem>
