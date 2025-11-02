<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import Chart from "./Chart.svelte";
	import Console from "./Console.svelte";
	import SideTab from "./SideTab.svelte";
	let parent: HTMLElement;
</script>

<div class="fcol-2 grow p-2 pt-0">
	<div class="frow-2 min-h-0 h-[70px]">
		<Console />
		<SideTab />
	</div>
	<div class="bg-slate-200 grow rounded relative" bind:this={parent}>
		{#if experiment_controller.experiment}
			{#each Object.values(experiment_controller.experiment.charts) as chart}
				<Chart bind:chart bind:parent />
			{/each}
		{/if}
	</div>
</div>
