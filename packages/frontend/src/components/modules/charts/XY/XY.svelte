<script lang="ts">
	import { onMount } from "svelte";
	import type { XYChartConfig, XYWebWorkerMessage } from "./XY_types";
	import { gstore } from "$states/global.svelte";

	let {
		id,
		config,
		width = $bindable(),
		height = $bindable(),
	}: {
		id: string;
		config: XYChartConfig;
		width: number;
		height: number;
	} = $props();
	let canvas: HTMLCanvasElement;
	const worker = new Worker(new URL("./XY_web_worker.js", import.meta.url), {
		type: "module",
	});

	$effect(() => {
		const message: XYWebWorkerMessage = {
			type: "resize",
			payload: {
				width,
				height,
			},
		};
		worker.postMessage(message);
	});

	onMount(() => {
		const offscreenCanvas = canvas.transferControlToOffscreen();

		const message: XYWebWorkerMessage = {
			type: "instantiate",
			payload: {
				canvas: offscreenCanvas,
				id,
				config: JSON.parse(JSON.stringify(config)),
				width,
				height,
			},
		};

		worker.postMessage(message, [offscreenCanvas]);

		gstore.experiments[id].chart_configs[config.title].reset = () => {
			worker.postMessage({ type: "reset" });
		};
	});
</script>

<canvas bind:this={canvas}></canvas>
