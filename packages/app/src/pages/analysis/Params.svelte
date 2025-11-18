<script lang="ts">
	import { analysis_controller, Tab } from "$controllers/analysis.svelte";
	import { onMount } from "svelte";

	import { cn } from "$components/utils.svelte";
	import ParamList from "$components/param/ParamList.svelte";
	import type { ArchivedParams } from "$controllers/params.svelte";
	import { ChevronDown, ChevronUp } from "@lucide/svelte";

	let { tab = $bindable() }: { tab: Tab } = $props();
</script>

{#snippet renderParam(k: string, p: ArchivedParams)}
	<div class="frow justify-between bg-white px-2 rounded">
		<div>{k}</div>
		<div>{p.value}</div>
	</div>
{/snippet}

<div class="title pl-1 pt-1">Params</div>
<div class="fcol-1 grow overflow-y-scroll scrollbar-slate-400">
	{#each Object.entries(tab.params) as [key, param]}
		{#if "value" in param}
			{@render renderParam(key, param as ArchivedParams)}
		{:else}
			<div
				class={cn(
					"fcol-1 bg-slate-700 rounded px-2 pt-1",
					tab.composite_opens[key] ? "pb-2" : "pb-1",
				)}
			>
				<button
					class="text-left text-white frow-2 justify-between items-center"
					onclick={() => {
						tab.composite_opens[key] = !tab.composite_opens[key];
					}}
					>{key}
					<div class="h-4 aspect-square text-white">
						{#if !tab.composite_opens[key]}
							<ChevronDown />
						{:else}
							<ChevronUp />
						{/if}
					</div>
				</button>
				{#if tab.composite_opens[key]}
					{#each Object.entries(param) as [_key, _param]}
						{@render renderParam(_key, _param)}
					{/each}
				{/if}
			</div>
		{/if}
	{/each}
</div>
