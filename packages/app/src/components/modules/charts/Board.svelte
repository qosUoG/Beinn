<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import Chart from "./Chart.svelte";
	let parent: HTMLElement;
</script>

<div class="bg-slate-300 flex-grow rounded-t relative" bind:this={parent}>
	{#each experiment_controller.instances_arr as experiment}
		{#each Object.values(experiment.charts) as chart}
			<Chart bind:chart bind:parent />
		{/each}
	{/each}
</div>
