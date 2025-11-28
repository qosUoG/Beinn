<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import { GripHorizontal } from "@lucide/svelte";

	import { move, resize } from "./attachments.svelte";
	import { onMount, type Snippet } from "svelte";

	let {
		parent = $bindable(),
		top,
		left,
		width,
		height,
		onresize,
		onmove,
		children,
		target = $bindable(),
		class: clazz,
		onmousedown,
		onmouseup,
	}: {
		parent: HTMLElement;
		top: number;
		left: number;
		width: number;
		height: number;
		onresize: ({
			width,
			height,
			top,
			left,
		}: {
			width: number;
			height: number;
			top: number;
			left: number;
		}) => void;
		onmove: ({ top, left }: { top: number; left: number }) => void;

		children: Snippet;
		class?: string;
		target: HTMLDivElement | undefined;

		onmousedown?: (target: HTMLDivElement) => void;
		onmouseup?: (target: HTMLDivElement) => void;
	} = $props();

	const getStyle = (
		v: "top" | "bottom" | null,
		h: "left" | "right" | null,
	) => {
		let style = "absolute mx-1   ";
		switch (h) {
			case "left":
				style += "w-2 -left-1 ";
				break;
			case "right":
				style += "w-2 -right-1 ";
				break;
			case null:
				style += "w-full left-0 ";
				break;
		}

		switch (v) {
			case "top":
				style += "h-2 -top-1 ";
				break;
			case "bottom":
				style += "h-2 -bottom-1 ";
				break;
			case null:
				style += "h-full top-0 ";
				break;
		}

		return style;
	};

	let moving = $state(false);

	function mouseupHandler() {
		moving = false;
		if (onmouseup) onmouseup(target!);
	}

	function mousedownHandler() {
		moving = true;
		if (onmousedown) onmousedown(target!);
	}

	onMount(() => {
		if (target)
			target.style = `top: ${top}px; left: ${left}px; width: ${width}px; height: ${height}px;`;
	});
</script>

<div
	class={cn("  absolute ", clazz)}
	bind:this={target}
	role={"chart wrapper"}
	onmouseup={() => {
		if (onmouseup) onmouseup(target!);
	}}
	onmousedown={(e) => {
		if (onmousedown) onmousedown(target!);
	}}
>
	<div
		class={cn("cursor-ns-resize", getStyle("top", null))}
		{@attach resize("top", null, parent, target, onresize)}
	></div>
	<div
		class={cn("cursor-ew-resize", getStyle(null, "right"))}
		{@attach resize(null, "right", parent, target, onresize)}
	></div>
	<div
		class={cn("cursor-ns-resize", getStyle("bottom", null))}
		{@attach resize("bottom", null, parent, target, onresize)}
	></div>
	<div
		class={cn("cursor-ew-resize", getStyle(null, "left"))}
		{@attach resize(null, "left", parent, target, onresize)}
	></div>

	<div
		class={cn("cursor-nwse-resize", getStyle("top", "left"))}
		{@attach resize("top", "left", parent, target, onresize)}
	></div>
	<div
		class={cn("cursor-nesw-resize", getStyle("top", "right"))}
		{@attach resize("top", "right", parent, target, onresize)}
	></div>
	<div
		class={cn("cursor-nwse-resize", getStyle("bottom", "right"))}
		{@attach resize("bottom", "right", parent, target, onresize)}
	></div>
	<div
		class={cn("cursor-nesw-resize", getStyle("bottom", "left"))}
		{@attach resize("bottom", "left", parent, target, onresize)}
	></div>

	<div
		role={"chart move"}
		class={cn(
			"absolute top-1 left-1/2 -translate-x-1/2 rounded w-6 text-center h-6 py-1 text-slate-600 bg-slate-200 ",
			moving
				? "cursor-grabbing **:cursor-grabbing"
				: "cursor-grab **:cursor-grab",
		)}
		{@attach move(parent, target, onmove, mouseupHandler, mousedownHandler)}
	>
		<GripHorizontal />
	</div>
	{@render children?.()}
</div>
