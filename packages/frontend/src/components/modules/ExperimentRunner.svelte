<script lang="ts">
	import Play from "$icons/Play.svelte";
	import { gstore } from "$states/global.svelte";

	let runnable_experiments = $derived(
		Object.values(gstore.experiments).filter(
			(experiment) =>
				experiment.name &&
				experiment.name.length > 0 &&
				JSON.stringify(experiment.params) ===
					JSON.stringify(experiment.temp_params) &&
				experiment.params !== undefined
		)
	);
</script>

<div class="container bg-slate-100 row-2">
	<div class="title wrapped bg-white flex items-center">Experiments</div>
	<div class="row-2 min-w-0 overflow-x-scroll">
		{#each runnable_experiments as experiment}
			<div class="wrapped bg-white row-1 items-center">
				<div class="wrapped bg-slat">{experiment.name}</div>
				<button class="icon-btn-sm green"><Play /></button>
			</div>
		{/each}
	</div>
</div>
