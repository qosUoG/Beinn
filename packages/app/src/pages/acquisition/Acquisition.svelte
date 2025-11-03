<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import Chart from "./chart/Chart.svelte";
	import Cli from "./Cli.svelte";
	import Panel from "./panel/Panel.svelte";
	import Note from "./Note.svelte";

	let parent: HTMLElement;
</script>

<div class="fcol-2 grow p-2 pt-0">
	{#if experiment_controller.experiment}
		<div class="frow-2 min-h-0 h-40">
			<div class="fcol-2">
				<Panel bind:experiment={experiment_controller.experiment} />
				<Note />
			</div>
			<Cli />
		</div>
		<div class="bg-slate-200 grow rounded relative" bind:this={parent}>
			{#if experiment_controller.experiment}
				{#each Object.values(experiment_controller.experiment.charts) as chart}
					<Chart bind:chart bind:parent />
				{/each}
			{/if}
		</div>
	{/if}
</div>
