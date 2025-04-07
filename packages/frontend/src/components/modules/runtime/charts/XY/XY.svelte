<script lang="ts">
	import { onMount } from "svelte";

	import { gstore } from "$states/global.svelte";
	import type { XYWebWorkerMessage } from "$states/chart.svelte";
	import type { XYChartConfig } from "qoslab-shared";

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
	const worker = new Worker(new URL("./worker.js", import.meta.url), {
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
	});
</script>

<canvas bind:this={canvas}></canvas>
