<script lang="ts">
	import Play from "$icons/Play.svelte";
	import ToggleRight from "$icons/ToggleRight.svelte";
	import { gstore } from "$states/global.svelte";
</script>

<div class="row-1">
	<div class="wrapped bg-slate-200 flex items-center">
		Selected Experiment
	</div>
	<div class="wrapped bg-slate-200 flex items-center">
		<!-- {gstore.experiment.path} -->
	</div>
	<button
		class="icon-btn bg-green-100 text-green-800"
		onclick={() => {
			// sendStartExperiment(gstore.workspace.path, gstore.experiment.path);
		}}><ToggleRight /></button>
	<button
		class="icon-btn bg-green-100 text-green-800"
		onclick={() => {
			// sendStartExperiment();
		}}><Play /></button>
</div>
