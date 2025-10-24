<script lang="ts">
	import DragResizeCard from "$components/dragresizecard/DragResizeCard.svelte";
	import type { Chart } from "$controllers/charts/charts.svelte";
	import { Circle, CircleSlash2, Eye, EyeOff } from "@lucide/svelte";
	import { onMount, untrack } from "svelte";

	let {
		chart = $bindable(),
		parent = $bindable(),
	}: { chart: Chart; parent: HTMLElement } = $props();

	let canvas: HTMLCanvasElement | undefined = $state(undefined);

	onMount(() => {
		if (canvas) chart.setCanvas(canvas.transferControlToOffscreen());
		return () => {
			chart.hide();
		};
	});

	let target: HTMLDivElement | undefined = $state(undefined);
</script>

<DragResizeCard
	bind:parent
	bind:target
	top={chart.top}
	left={chart.left}
	width={chart.width}
	height={chart.height}
	onmove={({ top, left }) => {
		chart.top = top;
		chart.left = left;
	}}
	onresize={({ width, height, top, left }) => {
		chart.width = width;
		chart.height = height;
		chart.top = top;
		chart.left = left;
	}}
	class="bg-white rounded">
	<div class="frow justify-between z-10 p-1">
		<div class="title bg-slate-200 wrapped w-fit">
			{chart.config.title}
		</div>
		<div>
			<button
				class="icon-btn-sm bg-gray-400 rounded text-gray-100"
				onclick={() => {
					if (!chart.showing && target)
						target.style.height = `${chart.height}px`;
					else if (target) target.style.height = "32px";
					chart.showing = !chart.showing;
				}}>
				{#if chart.showing}
					<Eye />
				{:else}
					<EyeOff />
				{/if}
			</button>
			<button
				class="icon-btn-sm bg-gray-400 rounded text-gray-100"
				onclick={() => {
					chart.is_drawing_points = !chart.is_drawing_points;
				}}>
				{#if chart.is_drawing_points}
					<Circle />
				{:else}
					<CircleSlash2 />
				{/if}
			</button>
		</div>
	</div>
	{#if chart.showing}
		<canvas bind:this={canvas} class="ml-2"></canvas>
	{/if}
</DragResizeCard>
