<script lang="ts">
	import { onMount } from "svelte";
	import type { ChartConfigs } from "../charts/type";
	import Xy from "../charts/XY/XY.svelte";
	import { watchresize } from "$components/utils.svelte";
	import DragResizeCard from "./DragResizeCard/DragResizeCard.svelte";

	let {
		chart_config,
		id,
		relative_parent,
	}: {
		id: string;
		chart_config: ChartConfigs;
		relative_parent: HTMLElement;
	} = $props();

	let width = $state(0);
	let height = $state(0);

	let canvas_wrapper: HTMLDivElement | undefined = $state(undefined);

	onMount(() => {
		if (canvas_wrapper) {
			width = canvas_wrapper.clientWidth;
			height = canvas_wrapper.clientHeight;
			console.log({ width, height });
		}
	});
</script>

<DragResizeCard {relative_parent}>
	<div class="title bg-slate-200 wrapped text-center w-fit">
		{chart_config.title}
	</div>

	<div class="absolute top-0 left-0 w-full h-full p-2 pt-8">
		<div
			class=" relative w-full h-full"
			bind:this={canvas_wrapper}
			use:watchresize
			ondivresize={({
				detail: { width: raw_width, height: raw_height },
			}) => {
				console.log({ raw_height, raw_width });
				width = raw_width;
				height = raw_height;
			}}>
			{#if canvas_wrapper}
				{#if chart_config.type === "XYPlot"}
					<Xy config={chart_config} {id} bind:width bind:height />
				{/if}
			{/if}
		</div>
	</div>
</DragResizeCard>
