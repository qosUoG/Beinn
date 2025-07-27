<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Flask from "$icons/Flask.svelte";
	import Settings from "$icons/Settings.svelte";
	import { mode_controller } from "./ModeController.svelte";
</script>

<div class="flex">
	<button
		class={cn(
			"  rounded-r-none icon-btn-sm",
			mode_controller.mode === "Configuration"
				? "bg-slate-500 text-slate-50"
				: "bg-slate-200"
		)}
		onclick={() => {
			mode_controller.mode = "Configuration";
		}}><Settings /></button>
	<button
		class={cn(
			" bg-slate-200 rounded-l-none icon-btn-sm",
			mode_controller.mode === "Runtime"
				? "bg-slate-500 text-slate-50"
				: "bg-slate-200"
		)}
		onclick={() => {
			mode_controller.mode = "Runtime";
		}}><Flask /></button>
</div>
