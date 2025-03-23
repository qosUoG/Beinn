<script lang="ts">
	import { onMount } from "svelte";
	import type { ChartConfigs } from "../charts/type";
	import Xy from "../charts/XY/XY.svelte";
	import { watchresize } from "$components/utils.svelte";

	let { chart_config, id }: { id: string; chart_config: ChartConfigs } =
		$props();

	let width = $state(0);
	let height = $state(0);

	let canvas_wrapper: HTMLDivElement;

	onMount(() => {
		width = canvas_wrapper.clientWidth;
		height = canvas_wrapper.clientHeight;
	});
</script>

<div
	class="w-full resize-y overflow-auto min-h-50 relative"
	bind:this={canvas_wrapper}
	use:watchresize
	ondivresize={({ detail: { width: raw_width, height: raw_height } }) => {
		console.log({ raw_height, raw_width });
		width = raw_width;
		height = raw_height;
	}}>
	{#if chart_config.type === "XYPlot"}
		<Xy config={chart_config} {id} bind:width bind:height />
	{/if}
</div>
