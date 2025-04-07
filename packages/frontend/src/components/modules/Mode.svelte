<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Flask from "$icons/Flask.svelte";
	import Settings from "$icons/Settings.svelte";
	import { gstore } from "$states/global.svelte";
</script>

<div class="flex">
	<button
		class={cn(
			"  rounded-r-none icon-btn",
			gstore.mode === "Configuration"
				? "bg-slate-500 text-slate-50"
				: "bg-slate-200"
		)}
		onclick={() => {
			gstore.mode = "Configuration";
		}}><Settings /></button>
	<button
		class={cn(
			" bg-slate-200 rounded-l-none icon-btn",
			gstore.mode === "Runtime"
				? "bg-slate-500 text-slate-50"
				: "bg-slate-200"
		)}
		onclick={() => {
			gstore.mode = "Runtime";
		}}><Flask /></button>
</div>
