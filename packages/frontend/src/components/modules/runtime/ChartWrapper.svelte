<script lang="ts">
	import { onMount } from "svelte";
	import { watchresize } from "$components/utils.svelte";
	import DragResizeCard from "./DragResizeCard.svelte";
	import type { ChartClass } from "$states/chart.svelte";

	let {
		chart = $bindable(),
		relative_parent,
	}: {
		chart: ChartClass;
		relative_parent: HTMLElement;
	} = $props();

	let canvas_wrapper: HTMLDivElement | undefined = $state(undefined);

	let canvas: HTMLCanvasElement | undefined = $state(undefined);

	onMount(() => {
		if (canvas_wrapper && canvas) {
			const offscreenCanvas = canvas.transferControlToOffscreen();
			chart.set_canvas({
				canvas: offscreenCanvas,
				width: 700,
				height: 400,
			});
		}

		chart.connect_ws();
	});
</script>

<DragResizeCard {relative_parent}>
	<div class="title bg-slate-200 wrapped text-center w-fit">
		{chart.title}
	</div>

	<div class="absolute top-0 left-0 w-full h-full p-2 pt-8">
		<div
			class=" relative w-full h-full"
			bind:this={canvas_wrapper}
			use:watchresize
			ondivresize={({ detail }) => {
				chart.resize(detail);
			}}>
			<canvas bind:this={canvas}></canvas>
		</div>
	</div>
</DragResizeCard>
