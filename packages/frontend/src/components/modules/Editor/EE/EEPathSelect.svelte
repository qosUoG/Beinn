<script lang="ts">
	import { clickoutside, cn } from "$components/utils.svelte";
	import { getRandomId } from "$lib/utils";
	import type { ModuleCls } from "qoslab-shared";
	import { tick } from "svelte";

	let {
		options,
		value = $bindable(),
	}: {
		value: ModuleCls;
		options: { cls: string; modules: string[] }[];
	} = $props();

	let open = $state(false);

	const id = getRandomId([]);
</script>

<button
	class="min-w-0 overflow-x-scroll text-nowrap w-full h-full"
	onclick={async (e) => {
		open = !open;
	}}
	{id}>
	{value}
</button>

{#if open}
	<div
		use:clickoutside={id}
		onoutsideclick={() => {
			open = false;
		}}
		class="absolute left-0 top-6 bg-white col z-10 shadow-xl rounded min-w-full">
		{#each options as { cls, modules }}
			<div class="hover:bg-slate-300">
				<div>{cls}</div>
				{#each modules as module}
					<button
						class={cn(
							" wrapped  text-nowrap text-left",
							value.module === module
								? "bg-slate-500 text-slate-50"
								: "hover:bg-slate-300"
						)}
						onclick={() => {
							value.module = module;
							value.cls = cls;
							open = false;
						}}>{module}</button>
				{/each}
			</div>
		{/each}
	</div>
{/if}
