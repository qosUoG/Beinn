<script lang="ts">
	import type { AllParamTypes } from "$controllers/params.svelte";
	import Composite from "./Composite.svelte";
	import Param from "./Param.svelte";

	let {
		param_opens,
		composite_opens = $bindable(),
		params = $bindable(),
		saveFn,
	}: {
		param_opens: boolean;
		composite_opens: Record<string, boolean>;
		params: Record<string, AllParamTypes>;
		saveFn: () => Promise<void>;
	} = $props();
</script>

{#if param_opens}
	<div
		class="fcol *:border-b-1 *:border-slate-400 border-2 border-t-0 border-slate-800">
		{#each Object.keys(params) as key}
			{#if params[key].type === "composite"}
				<Composite
					label={key}
					bind:open={composite_opens[key]}
					bind:params={params[key].children}
					{saveFn} />
			{:else}
				<Param label={key} bind:param={params[key]} {saveFn} />
			{/if}
		{/each}
	</div>
{/if}
