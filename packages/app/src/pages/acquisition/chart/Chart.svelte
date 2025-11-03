<script lang="ts">
	import DragResizeCard from "$components/dragresizecard/DragResizeCard.svelte";
	import type { Chart } from "$controllers/charts/chart.svelte";
	import { Circle, CircleSlash2, Eye, EyeOff } from "@lucide/svelte";
	import ChartCanvas from "./ChartCanvas.svelte";
	import { cn } from "$components/utils.svelte";

	import { Icon } from "@lucide/svelte";
	import { crosshairPlus } from "@lucide/lab";
	import { experiment_controller } from "$controllers/experiment.svelte";

	let {
		chart = $bindable(),
		parent = $bindable(),
	}: { chart: Chart; parent: HTMLElement } = $props();

	let target: HTMLDivElement | undefined = $state(undefined);

	$effect(() => {
		if (
			chart.config.title !==
			experiment_controller.experiment!.chart_in_focus
		)
			target!.style.zIndex = "0";
	});
</script>

<DragResizeCard
	bind:parent
	bind:target
	top={chart.top}
	left={chart.left}
	width={chart.width}
	height={chart.height}
	onmove={({ top, left }) => {
		chart.top = top;
		chart.left = left;
	}}
	onresize={({ width, height, top, left }) => {
		chart.width = width;
		chart.height = height;
		chart.top = top;
		chart.left = left;
	}}
	onmousedown={(target) => {
		experiment_controller.experiment!.chart_in_focus = chart.config.title;
		target.style.zIndex = "10";
	}}
	class="bg-white rounded border-slate-800 shadow-lg">
	<div class="fcol-2">
		<div class="frow justify-between p-1">
			<div class="title bg-slate-200 wrapped w-fit">
				{chart.config.title}
			</div>
			<div class="frow-1">
				<button
					class={cn(
						"border border-slate-400 px-2 h-full rounded text-[11px]",
						chart.auto_axis
							? "bg-slate-400 text-slate-50 cursor-default"
							: "text-slate-400"
					)}
					onclick={() => {
						if (chart.auto_axis) return;
						chart.auto_axis = true;
					}}>
					AUTO AXIS
				</button>
				<button
					class={cn(
						"icon-btn-sm border border-slate-400  rounded ",
						chart.tooltip_mode
							? "bg-slate-400 text-slate-50"
							: "text-slate-400"
					)}
					onclick={() => {
						chart.tooltip_mode = !chart.tooltip_mode;
					}}>
					<Icon iconNode={crosshairPlus} />
				</button>
				<button
					class="icon-btn-sm bg-slate-400 rounded text-slate-50"
					onclick={() => {
						if (!chart.showing && target)
							target.style.height = `${chart.height}px`;
						else if (target) target.style.height = "32px";
						chart.showing = !chart.showing;
					}}>
					{#if chart.showing}
						<Eye />
					{:else}
						<EyeOff />
					{/if}
				</button>
				<button
					class="icon-btn-sm bg-slate-400 rounded text-slate-50"
					onclick={() => {
						chart.is_drawing_points = !chart.is_drawing_points;
					}}>
					{#if chart.is_drawing_points}
						<Circle />
					{:else}
						<CircleSlash2 />
					{/if}
				</button>
			</div>
		</div>
		<!-- <div class=" w-6 bg-black" style={`height: ${chart.canvas_height}px`}>
		</div> -->
	</div>
	{#if chart.showing}
		<ChartCanvas bind:chart />
	{/if}
</DragResizeCard>
