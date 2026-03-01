<script lang="ts">
	import DragResizeCard from "$components/dragresizecard/DragResizeCard.svelte";
	import type { Chart } from "$controllers/charts/chart.svelte";
	import {
		Circle,
		CircleSlash2,
		Eye,
		EyeOff,
		Settings,
		X,
	} from "@lucide/svelte";
	import ChartCanvas from "./ChartCanvas.svelte";
	import { cn } from "$components/utils.svelte";

	import { Icon } from "@lucide/svelte";
	import { crosshairPlus } from "@lucide/lab";
	import { experiment_controller } from "$controllers/experiment.svelte";

	let {
		chart = $bindable(),
		parent = $bindable(),
	}: { chart: Chart; parent: HTMLElement } = $props();

	$effect(() => {
		if (
			chart.config.title !==
			experiment_controller.experiment!.chart_in_focus
		)
			chart.element!.style.zIndex = "0";
	});

	let chart_title_nospace = $derived(chart.config.title.replace(" ", ""));
</script>

<DragResizeCard
	bind:parent
	bind:target={chart.element}
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
	class={cn("bg-white rounded border-slate-800 shadow-lg")}
	style={`anchor-name:--${chart_title_nospace};`}
>
	<div
		id={chart.config.title}
		class={cn(" bg-white rounded p-1 absolute m-0 inset-auto")}
		style={`width: ${chart.width}px; height: ${chart.height}px; position-anchor:--${chart_title_nospace}; top: anchor(--${chart_title_nospace} top); left: anchor(--${chart_title_nospace} left);`}
		popover
	>
		<div class="fcol-4">
			<button
				class="icon-btn-sm bg-slate-400 rounded text-slate-50"
				popovertarget={chart.config.title}
				popovertargetaction="hide"
			>
				<X />
			</button>
			<div class="fcol-2 bg-slate-100 rounded p-2">
				<div class="title text-center">X Axis</div>
				<div class="frow flex-wrap gap-1 p-1">
					{#each chart.config.columns as column}
						<button
							class={cn(
								"border border-slate-600 text-slate-600 px-2 rounded",
								chart.x_axis === column
									? "text-slate-50 bg-slate-600"
									: "",
							)}
							onclick={() => {
								chart.set_x_axis(column);
							}}
						>
							{column}
						</button>
					{/each}
				</div>
			</div>
			<div class="fcol-2 bg-slate-100 rounded p-2">
				<div class="title text-center">Y Axis</div>
				<div class="frow flex-wrap gap-1 p-1">
					{#each chart.available_y_axis as column}
						<button
							class={cn(
								"border border-slate-600 text-slate-600 px-2 rounded",
								chart.y_axis.includes(column)
									? "text-slate-50 bg-slate-600"
									: "",
							)}
							onclick={() => {
								chart.toggle_y_axis(column);
							}}
						>
							{column}
						</button>
					{/each}
				</div>
			</div>
		</div>
	</div>

	<div class="fcol-2">
		<div class="frow justify-between p-1">
			<div class="frow-2">
				<div class="title bg-slate-200 wrapped w-fit">
					{chart.config.title}
				</div>
				<button
					class="icon-btn-sm bg-slate-400 rounded text-slate-50"
					popovertarget={chart.config.title}
				>
					<Settings />
				</button>
			</div>
			<div class="frow-1">
				<button
					class={cn(
						"border border-slate-400 px-2 h-full rounded text-[11px]",
						chart.auto_axis
							? "bg-slate-400 text-slate-50 cursor-default"
							: "text-slate-400",
					)}
					onclick={() => {
						if (chart.auto_axis) return;
						chart.auto_axis = true;
					}}
				>
					AUTO AXIS
				</button>
				<button
					class={cn(
						"icon-btn-sm border border-slate-400  rounded ",
						chart.tooltip_mode
							? "bg-slate-400 text-slate-50"
							: "text-slate-400",
					)}
					onclick={() => {
						chart.tooltip_mode = !chart.tooltip_mode;
					}}
				>
					<Icon iconNode={crosshairPlus} />
				</button>
				<button
					class="icon-btn-sm bg-slate-400 rounded text-slate-50"
					onclick={() => {
						if (!chart.showing && chart.element)
							chart.element.style.height = `${chart.height}px`;
						else if (chart.element)
							chart.element.style.height = "32px";
						chart.showing = !chart.showing;
					}}
				>
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
					}}
				>
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
