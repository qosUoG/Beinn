<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import Chart from "./Chart.svelte";
	import Console from "./Console.svelte";
	let parent: HTMLElement;
</script>

<div class="fcol-2 flex-grow p-2 pt-0">
	<div class="bg-slate-200 flex-grow rounded relative" bind:this={parent}>
		{#if experiment_controller.experiment}
			{#each Object.values(experiment_controller.experiment.charts) as chart}
				<Chart bind:chart bind:parent />
			{/each}
		{/if}
	</div>
	<div class="frow-2">
		<Console />
	</div>
</div>
