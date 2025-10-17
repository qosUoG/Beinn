<script lang="ts">
	import { type Store } from "@tauri-apps/plugin-store";
	import { cn } from "$components/utils.svelte";
	import { app_controller } from "$controllers/app.svelte";

	let store: Store;
</script>

<div class="min-h-[40px] frow w-full justify-center py-2">
	<div class="grid grid-cols-3 z-1000">
		<button
			class={cn(
				"px-2 text-center rounded-l",
				app_controller.page === "prepare"
					? "bg-slate-500 text-white"
					: "bg-slate-200"
			)}
			onclick={() => {
				app_controller.page = "prepare";
			}}>Preparation</button>
		<button
			class={cn(
				"px-2 text-center border-l border-slate-500",
				app_controller.page === "execute"
					? "bg-slate-500 text-white"
					: "bg-slate-200"
			)}
			onclick={() => {
				app_controller.page = "execute";
			}}>Experiment</button>
		<button
			class={cn(
				"px-2 text-center rounded-r border-l border-slate-500",
				app_controller.page === "analyze"
					? "bg-slate-500 text-white"
					: "bg-slate-200"
			)}
			onclick={() => {
				app_controller.page = "analyze";
			}}>Analysis</button>
	</div>
</div>
