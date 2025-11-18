<script lang="ts">
	import { ChevronDown, ChevronRight } from "@lucide/svelte";
	import Param from "./Param.svelte";
	import type {
		AllParamTypes,
		RuntimeAllParamTypes,
	} from "$controllers/params.svelte";

	let {
		label,
		params = $bindable(),
		open = $bindable(),
		saveFn,
		editable = true,
	}: {
		label: string;
		params:
			| Record<string, RuntimeAllParamTypes>
			| Record<string, AllParamTypes>;
		open: boolean;
		saveFn: () => Promise<void>;
		editable?: boolean;
	} = $props();
</script>

<button
	class=" py-1.5 underline underline-offset-2 text-left bg-slate-200 frow items-center"
	onclick={() => {
		open = !open;
	}}
>
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
		<Param label={key} bind:param={params[key]} {saveFn} {editable} />
	{/each}
{/if}
