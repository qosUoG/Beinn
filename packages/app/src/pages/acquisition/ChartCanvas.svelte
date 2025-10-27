<script lang="ts">
	import { onMount } from "svelte";
	import type { Chart } from "$controllers/charts/charts.svelte";

	let canvas: HTMLCanvasElement | undefined = $state(undefined);

	let { chart = $bindable() }: { chart: Chart } = $props();

	onMount(() => {
		if (canvas) chart.setCanvas(canvas.transferControlToOffscreen());
		return () => {
			chart.destroy();
		};
	});
</script>

<canvas bind:this={canvas} class="ml-2"></canvas>
