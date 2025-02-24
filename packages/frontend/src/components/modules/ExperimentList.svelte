<script lang="ts">
	import Plus from "$icons/Plus.svelte";

	import { getRandomId } from "$lib/utils";
	import { gstore } from "$states/global.svelte";
	import { editor } from "$components/modules/Editor/EditorController.svelte";
	import { tick } from "svelte";
</script>

<div class="container col-2 bg-slate-200">
	<div class="row justify-between items-center">
		<div class="title">Experiment</div>
		<button
			class="icon-btn-sm slate"
			onclick={async () => {
				const id = getRandomId(Object.keys(gstore.experiments));
				gstore.experiments[id] = { id };

				await tick();

				editor.id = id;
				editor.mode = "Experiment";
			}}><Plus /></button>
	</div>
	{#each Object.values(gstore.experiments) as experiment}
		{#if gstore.experiments.path !== undefined}
			<button class="container" id={`experiment-${experiment.id}`}>
				<div class="row-2">
					<div>Name</div>
					<div>{experiment.path}</div>
				</div>
			</button>
		{:else}
			<button
				class="container bg-white italic text-start text-slate-500/75"
				onclick={() => {
					editor.id = experiment.id;
					editor.mode = "Experiment";
				}}>Setup Experiment</button>
		{/if}
	{/each}
</div>
