<script>
	import { cn } from "$components/utils.svelte";
	import { analysis_controller } from "$controllers/analysis.svelte";
	import { ChevronDown, ChevronUp } from "@lucide/svelte";
</script>

<div class="bg-slate-200 h-full w-72 min-w-72 rounded fcol-1 p-1 pl-2">
	<div class="grid grid-cols-2 place-items-center gap-2 mr-2">
		<button
			class={cn(
				"bg-slate-700 text-slate-50 rounded pl-2 pr-1 w-full h-full frow items-center",
				analysis_controller.sort.startsWith("key")
					? "justify-between"
					: "justify-center"
			)}
			onclick={() => {
				if (analysis_controller.sort === "key_desc")
					analysis_controller.sort = "key_asc";
				else analysis_controller.sort = "key_desc";
			}}>
			Dataset
			{#if analysis_controller.sort.startsWith("key")}
				<span class="text-white icon-btn-sm">
					{#if analysis_controller.sort === "key_desc"}
						<ChevronDown />
					{:else if analysis_controller.sort === "key_asc"}
						<ChevronUp />
					{/if}
				</span>
			{/if}
		</button>
		<button
			class={cn(
				"bg-slate-700 text-slate-50 rounded pl-2 pr-1 w-full h-full frow items-center",
				analysis_controller.sort.startsWith("time")
					? "justify-between"
					: "justify-center"
			)}
			onclick={() => {
				if (analysis_controller.sort === "time_desc")
					analysis_controller.sort = "time_asc";
				else analysis_controller.sort = "time_desc";
			}}>
			Time of Creation
			{#if analysis_controller.sort.startsWith("time")}
				<span class="text-white icon-btn-sm">
					{#if analysis_controller.sort === "time_desc"}
						<ChevronDown />
					{:else if analysis_controller.sort === "time_asc"}
						<ChevronUp />
					{/if}
				</span>
			{/if}
		</button>
	</div>
	<div class="fcol-1 overflow-y-scroll scrollbar-slate-400">
		{#each analysis_controller.list as tab, i}
			{@const time_str = new Date(tab.time).toLocaleString()}
			<button
				class={cn(
					" rounded p-1 text-left grid grid-cols-2 bg-white border-2",
					tab.get_key() === analysis_controller.active_tab?.get_key()
						? "  border-slate-700 "
						: "border-white"
				)}
				onclick={() => {
					analysis_controller.active_tab_index = i;
				}}>
				<div class="text-start">
					{tab.get_key()}
				</div>
				<div class="text-center">
					{time_str}
				</div>
			</button>
		{/each}
	</div>
</div>
