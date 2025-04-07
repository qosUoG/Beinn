<script lang="ts">
	import { onMount } from "svelte";
	import Xy from "./charts/XY/XY.svelte";
	import { watchresize } from "$components/utils.svelte";
	import DragResizeCard from "./DragResizeCard/DragResizeCard.svelte";
	import type { Chart } from "$states/chart.svelte";

	let {
		chart,
		id,
		relative_parent,
	}: {
		id: string;
		chart: Chart;
		relative_parent: HTMLElement;
	} = $props();

	let width = $state(0);
	let height = $state(0);

	let canvas_wrapper: HTMLDivElement | undefined = $state(undefined);

	onMount(() => {
		if (canvas_wrapper) {
			width = canvas_wrapper.clientWidth;
			height = canvas_wrapper.clientHeight;
		}
	});
</script>

<DragResizeCard {relative_parent}>
	<div class="title bg-slate-200 wrapped text-center w-fit">
		{chart.config.title}
	</div>

	<div class="absolute top-0 left-0 w-full h-full p-2 pt-8">
		<div
			class=" relative w-full h-full"
			bind:this={canvas_wrapper}
			use:watchresize
			ondivresize={({
				detail: { width: raw_width, height: raw_height },
			}) => {
				width = raw_width;
				height = raw_height;
			}}>
			{#if canvas_wrapper}
				{#if chart.config.type === "XYPlot"}
					<Xy config={chart.config} {id} bind:width bind:height />
				{/if}
			{/if}
		</div>
	</div>
</DragResizeCard>
