<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import { GripHorizontal } from "@lucide/svelte";

	import { move, resize } from "./attachments.svelte";

	let {
		parent = $bindable(),
		onresize,
		onmove,
	}: {
		parent: HTMLElement;
		onresize: ({
			width,
			height,
		}: {
			width: number;
			height: number;
		}) => void;
		onmove: ({ top, left }: { top: number; left: number }) => void;
	} = $props();

	let target: HTMLDivElement | undefined = $state(undefined);

	const getStyle = (
		v: "top" | "bottom" | null,
		h: "left" | "right" | null
	) => {
		let style = "absolute mx-1 ";
		switch (h) {
			case "left":
				style += "w-3.5 -left-1 ";
				break;
			case "right":
				style += "w-3.5 -right-1 ";
				break;
			case null:
				style += "w-full left-0 ";
				break;
		}

		switch (v) {
			case "top":
				style += "h-3.5 -top-1 ";
				break;
			case "bottom":
				style += "h-3.5 -bottom-1 ";
				break;
			case null:
				style += "h-full top-0 ";
				break;
		}

		return style;
	};

	let moving = $state(false);
</script>

<div class={cn(" bg-white absolute ")} bind:this={target}>
	<div
		class={cn("cursor-ns-resize", getStyle("top", null))}
		{@attach resize("top", null, target, onresize)}>
	</div>
	<div
		class={cn("cursor-ew-resize", getStyle(null, "right"))}
		{@attach resize(null, "right", target, onresize)}>
	</div>
	<div
		class={cn("cursor-ns-resize", getStyle("bottom", null))}
		{@attach resize("bottom", null, target, onresize)}>
	</div>
	<div
		class={cn("cursor-ew-resize", getStyle(null, "left"))}
		{@attach resize(null, "left", target, onresize)}>
	</div>

	<div
		class={cn("cursor-nwse-resize", getStyle("top", "left"))}
		{@attach resize("top", "left", target, onresize)}>
	</div>
	<div
		class={cn("cursor-nesw-resize", getStyle("top", "right"))}
		{@attach resize("top", "right", target, onresize)}>
	</div>
	<div
		class={cn("cursor-nwse-resize", getStyle("bottom", "right"))}
		{@attach resize("bottom", "right", target, onresize)}>
	</div>
	<div
		class={cn("cursor-nesw-resize", getStyle("bottom", "left"))}
		{@attach resize("bottom", "left", target, onresize)}>
	</div>

	<div
		class={cn(
			"absolute top-1 left-1/2 -translate-x-1/2 rounded w-6 text-center h-6 py-1 text-slate-600 bg-slate-200 z-1",
			moving
				? "cursor-grabbing **:cursor-grabbing"
				: "cursor-grab **:cursor-grab",
			getStyle("top", null)
		)}
		{@attach move(parent, target, moving, onmove)}>
		<GripHorizontal />
	</div>
</div>
