<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import Chart from "./Chart.svelte";
	let parent: HTMLElement;
</script>

<div class="bg-slate-300 flex-grow rounded-t relative" bind:this={parent}>
	{#if experiment_controller.experiment}
		{#each Object.values(experiment_controller.experiment.charts) as chart}
			<Chart bind:chart bind:parent />
		{/each}
	{/if}
</div>
