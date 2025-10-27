<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import { app_controller } from "$controllers/app.svelte";
	import Logger from "./Logger.svelte";
</script>

<div class="min-h-[40px] frow-4 py-2 m-auto justify-between w-1/2">
	<div class="frow-2 z-1000">
		<div class="grid grid-cols-2">
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
					"px-2 text-center border-l rounded-r border-slate-500",
					app_controller.page === "execute"
						? "bg-slate-500 text-white"
						: "bg-slate-200"
				)}
				onclick={() => {
					app_controller.page = "execute";
				}}>Acquisition</button>
		</div>

		<button
			class={cn(
				"px-2 text-center rounded ",
				app_controller.page === "analyze"
					? "bg-slate-500 text-white"
					: "bg-slate-200"
			)}
			onclick={() => {
				app_controller.page = "analyze";
			}}>Analysis</button>
	</div>

	<Logger />
</div>
