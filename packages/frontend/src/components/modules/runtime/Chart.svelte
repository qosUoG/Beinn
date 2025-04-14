<script lang="ts">
	import { onMount } from "svelte";
	import { watchresize } from "$components/utils.svelte";
	import DragResizeCard from "./DragResizeCard.svelte";
	import type { ChartClass } from "$states/chart.svelte";
	import DotFilled from "$icons/DotFilled.svelte";
	import DotEmpty from "$icons/DotEmpty.svelte";

	let {
		chart = $bindable(),
		relative_parent,
	}: {
		chart: ChartClass;
		relative_parent: HTMLElement;
	} = $props();

	let canvas: HTMLCanvasElement;

	onMount(() => {
		const offscreenCanvas = canvas.transferControlToOffscreen();
		chart.set_canvas({
			canvas: offscreenCanvas,
			width: 700,
			height: 400,
		});
	});
</script>

<DragResizeCard {relative_parent}>
	<div class="frow justify-between z-100000">
		<div class="title bg-slate-200 wrapped w-fit">
			{chart.title}
		</div>
		<div>
			<button
				class="btn-sm-icon bg-gray-400 rounded text-gray-100"
				onclick={() => {
					if (chart.is_drawing_points) chart.disable_draw_points();
					else chart.enable_draw_points();
				}}>
				{#if chart.is_drawing_points}
					<DotFilled />
				{:else}
					<DotEmpty />
				{/if}
			</button>
		</div>
	</div>

	<div class="absolute top-6 left-0 w-full h-full p-2 pb-8">
		<div
			class=" relative w-full h-full"
			use:watchresize
			ondivresize={({ detail }) => {
				chart.resize(detail);
			}}>
			<canvas bind:this={canvas}></canvas>
		</div>
	</div>
</DragResizeCard>
