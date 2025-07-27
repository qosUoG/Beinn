<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Grip from "$icons/Grip.svelte";
	import type { Snippet } from "svelte";
	import type { Action } from "svelte/action";

	let {
		children,
		relative_parent,
	}: { children: Snippet; relative_parent: HTMLElement } = $props();

	let target_node: HTMLDivElement;

	const moveable_state = $state({
		moving: false,
		position: {
			top: 0,
			left: 0,
		},
		mouse: {
			x: 0,
			y: 0,
		},
	});

	const movehandle: Action<Element, undefined, {}> = (node) => {
		const handlemousemove = (e: MouseEvent) => {
			if (!moveable_state.moving) return;

			const new_top =
				moveable_state.position.top +
				e.clientY -
				moveable_state.mouse.y;
			const new_left =
				moveable_state.position.left +
				e.clientX -
				moveable_state.mouse.x;

			if (new_top >= 8) target_node.style.top = `${new_top}px`;
			else target_node.style.top = `8px`;
			if (new_left >= 8) target_node.style.left = `${new_left}px`;
			else target_node.style.left = `8px`;
		};

		const handlemouseup = (e: MouseEvent) => {
			moveable_state.moving = false;
		};

		$effect(() => {
			window.addEventListener("mousemove", handlemousemove);
			window.addEventListener("mouseup", handlemouseup);

			return () => {
				window.removeEventListener("mousemove", handlemousemove);
				window.removeEventListener("mouseup", handlemouseup);
			};
		});
	};

	const resizeable_state: {
		horizontal: {
			resizing: boolean;
			width: number;
			left: number;
			direction: "left" | "right";
			mouse_x: number;
		};

		vertical: {
			resizing: boolean;
			height: number;
			top: number;
			direction: "top" | "bottom";
			mouse_y: number;
		};
	} = $state({
		horizontal: {
			resizing: false,
			width: 0,
			left: 0,
			direction: "left",
			mouse_x: 0,
		},

		vertical: {
			resizing: false,
			height: 0,
			top: 0,
			direction: "top",
			mouse_y: 0,
		},
	});

	const resizehandle: Action<Element, undefined, {}> = (node) => {
		const handlemousemove = (e: MouseEvent) => {
			if (resizeable_state.vertical.resizing) {
				const delta = e.clientY - resizeable_state.vertical.mouse_y;
				// Resizing with the bottom handle
				if (resizeable_state.vertical.direction === "bottom") {
					const new_height = resizeable_state.vertical.height + delta;
					if (new_height > 0)
						target_node.style.height = `${new_height}px`;
					else target_node.style.height = `1px`;
				} else {
					const new_top = resizeable_state.vertical.top + delta;

					const new_height = resizeable_state.vertical.height - delta;

					if (new_top >= 8) {
						if (new_height >= 24)
							target_node.style.height = `${new_height}px`;
						else target_node.style.height = `24px`;

						target_node.style.top = `${new_top}px`;
					} else {
						// Mouse moved out of bound
						target_node.style.top = `8px`;
						// Height becomes the difference between bottom and top
						const { top, bottom } =
							target_node.getBoundingClientRect();
						target_node.style.height = `${bottom - top}px`;
					}
				}
			}

			if (resizeable_state.horizontal.resizing) {
				const delta = e.clientX - resizeable_state.horizontal.mouse_x;
				// Resizing with the bottom handle
				if (resizeable_state.horizontal.direction === "right") {
					const new_width = resizeable_state.horizontal.width + delta;

					if (new_width > 0)
						target_node.style.width = `${new_width}px`;
					else target_node.style.width = `1px`;
				} else {
					const new_left = resizeable_state.horizontal.left + delta;

					const new_width = resizeable_state.horizontal.width - delta;

					if (new_left >= 8) {
						if (new_width >= 24)
							target_node.style.width = `${new_width}px`;
						else target_node.style.width = `24px`;

						target_node.style.left = `${new_left}px`;
					} else {
						// Mouse moved out of bound
						target_node.style.left = `8px`;
						// Height becomes the difference between bottom and left
						const { left, right } =
							target_node.getBoundingClientRect();
						target_node.style.width = `${right - left}px`;
					}
				}
			}
		};

		const handlemouseup = () => {
			resizeable_state.vertical.resizing = false;
			resizeable_state.horizontal.resizing = false;
		};

		$effect(() => {
			window.addEventListener("mousemove", handlemousemove);
			window.addEventListener("mouseup", handlemouseup);

			return () => {
				window.removeEventListener("mousemove", handlemousemove);
				window.removeEventListener("mouseup", handlemouseup);
			};
		});
	};

	function vMousedownHandler(e: MouseEvent, top?: number) {
		const { height } = target_node.getBoundingClientRect();

		resizeable_state.vertical = {
			resizing: true,
			height,
			top: top ?? 0,
			direction: top === undefined ? "bottom" : "top",
			mouse_y: e.clientY,
		};
	}

	function tMousedownHandler(e: MouseEvent) {
		vMousedownHandler(
			e,
			target_node.getBoundingClientRect().top -
				relative_parent.getBoundingClientRect().top
		);
	}

	function bMousedownHandler(e: MouseEvent) {
		vMousedownHandler(e);
	}

	function hMousedownHandler(e: MouseEvent, left?: number) {
		const { width } = target_node.getBoundingClientRect();

		resizeable_state.horizontal = {
			resizing: true,
			width,
			left: left ?? 0,
			direction: left === undefined ? "right" : "left",
			mouse_x: e.clientX,
		};
	}

	function lMousedownHandler(e: MouseEvent) {
		hMousedownHandler(
			e,
			target_node.getBoundingClientRect().left -
				relative_parent.getBoundingClientRect().left
		);
	}

	function rMousedownHandler(e: MouseEvent) {
		hMousedownHandler(e);
	}

	function tlMousedownHandler(e: MouseEvent) {
		tMousedownHandler(e);
		lMousedownHandler(e);
	}

	function trMousedownHandler(e: MouseEvent) {
		tMousedownHandler(e);
		rMousedownHandler(e);
	}

	function brMousedownHandler(e: MouseEvent) {
		bMousedownHandler(e);
		rMousedownHandler(e);
	}

	function blMousedownHandler(e: MouseEvent) {
		bMousedownHandler(e);
		lMousedownHandler(e);
	}
</script>

<div
	class="bg-white section absolute top-2 left-2 w-256 h-128"
	bind:this={target_node}>
	<!-- Top -->
	<button
		aria-label="top-resize"
		class="absolute h-3.5 w-full -top-1 left-0 cursor-ns-resize mx-1"
		use:resizehandle
		onmousedown={tMousedownHandler}></button>

	<!-- Right -->
	<button
		aria-label="right-resize"
		class="absolute h-full w-3.5 -right-1 top-0 cursor-ew-resize my-1"
		use:resizehandle
		onmousedown={rMousedownHandler}></button>

	<!-- Bottom -->
	<button
		aria-label="bottom-resize"
		class="absolute h-3.5 w-full -bottom-1 left-0 cursor-ns-resize mx-1"
		use:resizehandle
		onmousedown={bMousedownHandler}></button>

	<!-- Left -->
	<button
		aria-label="left-resize"
		class="absolute h-full w-3.5 -left-1 top-0 cursor-ew-resize my-1"
		use:resizehandle
		onmousedown={lMousedownHandler}></button>

	<!-- Top Left Corner -->
	<button
		aria-label="topleft-resize"
		class="absolute h-3.5 w-3.5 -top-1 -left-1 cursor-nwse-resize"
		use:resizehandle
		onmousedown={tlMousedownHandler}></button>

	<!-- Top Right Corner -->
	<button
		aria-label="topright-resize"
		class="absolute h-3.5 w-3.5 -top-1 -right-1 cursor-nesw-resize"
		use:resizehandle
		onmousedown={trMousedownHandler}></button>

	<!-- Bottom Right Corner -->
	<button
		aria-label="bottomright-resize"
		class="absolute h-3.5 w-3.5 -bottom-1 -right-1 cursor-nwse-resize"
		use:resizehandle
		onmousedown={brMousedownHandler}>
	</button>

	<!-- Bottom Left Corner -->
	<button
		aria-label="bottomleft-resize"
		class="absolute h-3.5 w-3.5 -bottom-1 -left-1 cursor-nesw-resize"
		use:resizehandle
		onmousedown={blMousedownHandler}>
	</button>

	<!-- Top Drag Bar -->
	<button
		class={cn(
			" absolute top-1 left-1/2 -translate-x-1/2 rounded w-6 text-center h-6 py-1 text-slate-600 bg-slate-200 z-100000",
			moveable_state.moving
				? "cursor-grabbing **:cursor-grabbing"
				: "cursor-grab **:cursor-grab"
		)}
		use:movehandle
		onmousedown={(e: MouseEvent) => {
			moveable_state.moving = true;
			const { top, left } = target_node.getBoundingClientRect();
			const { top: parent_top, left: parent_left } =
				relative_parent.getBoundingClientRect();
			moveable_state.position.top = top - parent_top;
			moveable_state.position.left = left - parent_left;
			moveable_state.mouse.x = e.clientX;
			moveable_state.mouse.y = e.clientY;
		}}><Grip /></button>

	{@render children?.()}
</div>
