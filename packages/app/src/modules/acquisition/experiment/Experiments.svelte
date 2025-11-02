<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import ExperimentItem from "./ExperimentItem.svelte";
	import NewExperiment from "./NewExperiment.svelte";
</script>

{#if workspace_controller.connection === "connected"}
	<div class="justify-between fcol-2 min-h-0 h-full">
		<div
			class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2 grow pb-8">
			{#each experiment_controller.instances_arr as experiment}
				<ExperimentItem bind:experiment />
			{/each}
		</div>
		<NewExperiment />
	</div>
{/if}
