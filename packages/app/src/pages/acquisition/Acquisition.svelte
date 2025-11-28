<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import Chart from "./chart/Chart.svelte";
	import Cli from "./Cli.svelte";
	import Panel from "./panel/Panel.svelte";
	import Note from "./Note.svelte";

	let parent: HTMLElement;
	let move_context = $state({
		moving: false,
		x: 0,
		y: 0,
	});

	function mousedownHandler(m: MouseEvent) {
		move_context.moving = true;
		move_context.x = m.clientX;
		move_context.y = m.clientY;
	}

	function mouseupHandler(m: MouseEvent) {
		move_context.moving = false;
		move_context.x = 0;
		move_context.y = 0;
	}

	function mousemoveHandler(m: MouseEvent) {
		if (!move_context.moving || !experiment_controller.experiment) return;

		for (const chart of Object.values(
			experiment_controller.experiment.charts,
		)) {
			chart.left += m.clientX - move_context.x;
			chart.top += m.clientY - move_context.y;
		}
	}
</script>

<div class="frow-2 grow p-2 pt-0">
	{#if experiment_controller.experiment}
		<div class="fcol-2 min-h-0 h-full w-lg min-w-lg">
			<Panel bind:experiment={experiment_controller.experiment} />
			<div class="grid gap-2 grid-cols-1 grow min-h-0">
				<Note />
				<Cli />
			</div>
		</div>
		<div
			class="bg-slate-200 grow rounded relative"
			bind:this={parent}
			onmousedown={mousedownHandler}
			onmouseup={mouseupHandler}
			onmousemove={mousemoveHandler}
			role={"chart panning"}
		>
			{#if experiment_controller.experiment}
				{#each Object.keys(experiment_controller.experiment.charts) as name}
					<Chart
						bind:chart={
							experiment_controller.experiment.charts[name]
						}
						bind:parent
					/>
				{/each}
			{/if}
		</div>
	{/if}
</div>
