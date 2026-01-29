<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import Chart from "./chart/Chart.svelte";
	import Cli from "./Cli.svelte";
	import Panel from "./panel/Panel.svelte";
	import Note from "./Note.svelte";

	let parent: HTMLElement | undefined = $state(undefined);
	let move_context: {
		moving: boolean;
		chart_positions: Record<
			string,
			{
				t: number;
				l: number;
				x: number;
				y: number;
			}
		>;
	} = $state({
		moving: false,
		chart_positions: {},
	});

	function mousedownHandler(m: MouseEvent) {
		move_context.moving = true;

		for (const [name, chart] of Object.entries(
			experiment_controller.experiment!.charts,
		)) {
			const { left, top } = chart.element!.getBoundingClientRect();
			const { left: parent_left, top: parent_top } =
				parent!.getBoundingClientRect();

			move_context.chart_positions[name] = {
				t: top - parent_top,
				l: left - parent_left,
				x: m.clientX,
				y: m.clientY,
			};
		}
		m.stopImmediatePropagation();
	}

	function mouseupHandler(m: MouseEvent) {
		move_context.moving = false;
		move_context.chart_positions = {};
	}

	function mousemoveHandler(m: MouseEvent) {
		if (!move_context.moving || !experiment_controller.experiment) return;

		for (const [name, chart] of Object.entries(
			experiment_controller.experiment.charts,
		)) {
			const r = move_context.chart_positions[name];

			let top = r.t + m.clientY - r.y;
			let left = r.l + m.clientX - r.x;

			chart.element!.style.top = `${top}px`;
			chart.element!.style.left = `${left}px`;

			chart.element!.style.left = `${left}px`;
			chart.element!.style.top = `${top}px`;

			chart.left = left;
			chart.top = top;
		}

		m.stopImmediatePropagation();
	}
</script>

<div class="frow-2 grow p-2 pt-0 min-h-0">
	{#if experiment_controller.experiment}
		<div class="fcol-2 min-h-0 h-full w-lg min-w-lg">
			<Panel bind:experiment={experiment_controller.experiment} />
			<div class="grid gap-2 grid-rows-2 grow min-h-0">
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
			role={"chart panning"}>
			{#if experiment_controller.experiment}
				{#each Object.keys(experiment_controller.experiment.charts) as name}
					<Chart
						bind:chart={
							experiment_controller.experiment.charts[name]
						}
						bind:parent />
				{/each}
			{/if}
		</div>
	{/if}
</div>
