<script lang="ts">
	import { type ChartConfiguration } from "chart.js";
	import { onMount } from "svelte";

	let {}: {} = $props();

	let canvas: HTMLCanvasElement;

	const worker = new Worker(new URL("./XY_web_worker.js", import.meta.url), {
		type: "module",
	});
	onMount(() => {
		const offscreenCanvas = canvas.transferControlToOffscreen();
		worker.postMessage({ canvas: offscreenCanvas }, [offscreenCanvas]);
	});
</script>

<canvas bind:this={canvas}></canvas>
