<script lang="ts">
	import type { CompositeParam } from "$controllers/params.svelte";
	import { ChevronDown, ChevronRight } from "@lucide/svelte";
	import Param from "./Param.svelte";

	let {
		label,
		params = $bindable(),
		open = $bindable(),
		saveFn,
	}: {
		label: string;
		params: CompositeParam["children"];
		open: boolean;
		saveFn: () => Promise<void>;
	} = $props();
</script>

<button
	class=" py-1.5 underline underline-offset-2 text-left bg-slate-200 frow items-center"
	onclick={() => {
		open = !open;
	}}>
	<span class="h-3">
		{#if !open}
			<ChevronRight strokeWidth="3px" />
		{:else}
			<ChevronDown strokeWidth="3px" />
		{/if}
	</span>
	{label}
</button>

{#if open}
	{#each Object.keys(params) as key}
		<Param label={key} bind:param={params[key]} {saveFn} />
	{/each}
{/if}
