<script lang="ts">
	import type {
		AllParamTypes,
		RuntimeAllParamTypes,
	} from "$controllers/params.svelte";
	import Composite from "./Composite.svelte";
	import Param from "./Param.svelte";

	let {
		param_opens,
		composite_opens = $bindable(),
		params = $bindable(),
		saveFn,
		editable = true,
	}: {
		param_opens: boolean;
		composite_opens: Record<string, boolean>;
		params:
			| Record<
					string,
					RuntimeAllParamTypes | Record<string, RuntimeAllParamTypes>
			  >
			| Record<string, AllParamTypes | Record<string, AllParamTypes>>;
		saveFn: () => Promise<void>;
		editable?: boolean;
	} = $props();
</script>

{#if param_opens}
	<div
		class="fcol *:border-b *:border-slate-400 border-2 border-t-0 border-slate-800 min-w-80"
	>
		{#each Object.keys(params) as key}
			{#if !("type" in params[key])}
				<Composite
					label={key}
					bind:open={composite_opens[key]}
					bind:params={params[key]}
					{saveFn}
					{editable}
				/>
			{:else}
				<Param
					label={key}
					bind:param={params[key] as RuntimeAllParamTypes}
					{saveFn}
					{editable}
				/>
			{/if}
		{/each}
	</div>
{/if}
