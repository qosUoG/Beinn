<script lang="ts">
	import DragResizeCard from "$components/dragresizecard/DragResizeCard.svelte";
	import type { Chart } from "$controllers/charts/charts.svelte";
	import { Circle, CircleSlash2 } from "@lucide/svelte";

	let {
		chart = $bindable(),
		parent = $bindable(),
	}: { chart: Chart; parent: HTMLElement } = $props();

	let canvas: HTMLCanvasElement;
	$effect(() => {
		if (canvas) chart.setCanvas(canvas.transferControlToOffscreen());
	});
</script>

<DragResizeCard
	bind:parent
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
	}}>
	<div class="frow justify-between z-10 p-1">
		<div class="title bg-slate-200 wrapped w-fit">
			{chart.config.title}
		</div>
		<div>
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
	<canvas bind:this={canvas} class="ml-2"></canvas>
	<!-- <div class="absolute top-6 left-0 w-full h-full p-2 pb-8">
		<div class=" relative w-full h-full">
			<canvas bind:this={canvas}></canvas>
		</div>
	</div> -->
</DragResizeCard>
