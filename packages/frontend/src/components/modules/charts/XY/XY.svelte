<script lang="ts">
	import { onMount } from "svelte";
	import type { XYChartConfig, XYEvent } from "./XY_types";

	let {
		mode,
		url,
		config,
	}: {
		mode: XYEvent["payload"]["mode"];
		url: string;
		config: XYChartConfig;
	} = $props();

	let canvas: HTMLCanvasElement;

	const worker = new Worker(new URL("./XY_web_worker.js", import.meta.url), {
		type: "module",
	});
	onMount(() => {
		const offscreenCanvas = canvas.transferControlToOffscreen();

		const payload: XYEvent = {
			type: "instantiate",
			payload: {
				canvas: offscreenCanvas,
				mode,
				url,
				config,
			},
		};

		worker.postMessage({ canvas: offscreenCanvas }, [offscreenCanvas]);
	});
</script>

<canvas bind:this={canvas}></canvas>
