<script lang="ts">
	import {
		experiment_controller,
		type Experiment,
	} from "$controllers/ExperimentController.svelte";

	import BaseItem from "../_ee/BaseItem.svelte";

	let { experiment = $bindable() }: { experiment: Experiment } = $props();
</script>

<BaseItem bind:ee={experiment} controller={experiment_controller} />
