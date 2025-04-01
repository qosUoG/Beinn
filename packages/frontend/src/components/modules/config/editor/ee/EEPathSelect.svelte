<script lang="ts">
	import Separator from "$components/reuseables/Separator.svelte";
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

<div class="frow-2 bg-white wrapped flex-grow min-w-0 h-full">
	<div class="editor-label">Class</div>
	<Separator />
	<div class="relative flex-grow -mx-2 px-2 min-w-0">
		<button
			class="w-full h-full text-left"
			onclick={async (e) => {
				open = !open;
			}}
			{id}>
			{#if value.module !== "" && value.cls !== ""}
				from {value.module} import
				{value.cls}
			{/if}
		</button>

		{#if open}
			<div
				use:clickoutside={id}
				onoutsideclick={() => {
					open = false;
				}}
				class=" absolute left-0 top-6 bg-white fcol z-10 shadow-xl rounded min-w-full">
				{#each options as { cls, modules }}
					<div class={cn(" wrapped fcol group")}>
						<div
							class={cn(
								" wrapped ",
								value.cls === cls
									? "bg-slate-500 text-slate-50"
									: "group-hover:bg-slate-300"
							)}>
							{cls}
						</div>
						{#each modules as module}
							<button
								class={cn(
									"   text-nowrap text-left ml-6 wrapped flex-grow",
									value.module === module
										? "bg-slate-500 text-slate-50"
										: "hover:bg-slate-300"
								)}
								onclick={() => {
									value.module = module;
									value.cls = cls;
									open = false;
								}}>
								{module}
							</button>
						{/each}
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
