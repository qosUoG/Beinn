<script lang="ts">
	import { onMount } from "svelte";
	import type { Chart } from "$controllers/charts/chart.svelte";
	import { throttle } from "$lib/utils";

	let canvas: HTMLCanvasElement | undefined = $state(undefined);

	let { chart = $bindable() }: { chart: Chart } = $props();

	onMount(() => {
		if (canvas) chart.onMount(canvas.transferControlToOffscreen());
		return () => {
			chart.onUnmount();
		};
	});

	const handleWheel = throttle((e: WheelEvent) => {
		let direction: "in" | "out" = e.deltaY > 0 ? "in" : "out";

		if (x_down) chart.zoom(direction, e.offsetX - 8, undefined);
		else if (y_down) chart.zoom(direction, undefined, e.offsetY);
		else chart.zoom(direction, e.offsetX - 8, e.offsetY);

		chart.auto_axis = false;
	}, 100);

	let is_panning = $state(false);

	let old_x = $state(0);
	let old_y = $state(0);

	function handleMouseDown(e: MouseEvent) {
		is_panning = true;
		old_x = e.offsetX - 8;
		old_y = e.offsetY;

		e.stopImmediatePropagation();
	}

	function handleMouseUp(e: MouseEvent) {
		is_panning = false;
	}

	function handleMouseMove(e: MouseEvent) {
		if (chart.tooltip_mode) chart.enableTooltip(e.offsetX - 8, e.offsetY);

		if (!is_panning) return;
		chart.pan(old_x, old_y, e.offsetX - 8, e.offsetY);
		old_x = e.offsetX - 8;
		old_y = e.offsetY;

		chart.auto_axis = false;

		e.stopImmediatePropagation();
	}

	let x_down = $state(false);
	let y_down = $state(false);

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === "x") x_down = true;
		else if (e.key === "y") y_down = true;
	}

	function handleKeyUp(e: KeyboardEvent) {
		if (e.key === "x") x_down = false;
		else if (e.key === "y") y_down = false;
	}
</script>

<svelte:window
	onmouseup={handleMouseUp}
	onkeyup={handleKeyUp}
	onkeydown={handleKeyDown} />

<div
	role={"canvas control"}
	onwheel={handleWheel}
	onmousedown={handleMouseDown}
	onmousemove={handleMouseMove}>
	<canvas bind:this={canvas} class="ml-2"></canvas>
</div>
