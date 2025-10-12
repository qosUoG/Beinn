<script lang="ts" generics="T extends Instance, U extends EEBaseController<T>">
	import {
		Check,
		ChevronDown,
		ChevronRight,
		FolderSync,
		Trash2,
		Undo,
	} from "@lucide/svelte";
	import Param from "../_ee/Param.svelte";
	import Composite from "../_ee/Composite.svelte";

	import type { Snippet } from "svelte";
	import { cn } from "$components/utils.svelte";
	import { deepCopy } from "$lib/utils";
	import type {
		EEBaseController,
		Instance,
	} from "$controllers/eebase.svelte";

	let {
		ee = $bindable(),
		controller,
		deletable = $bindable(),
		children,
	}: {
		ee: T;
		controller: U;
		deletable: boolean;
		children?: Snippet;
	} = $props();
</script>

<div class="bg-slate-50 rounded fcol-1 p-1">
	<div class="flex items-center w-full justify-between">
		<div
			class="  font-light text-slate-950 h-full flex items-center px-1 rounded text-sm">
			{ee.name}
		</div>

		<div>
			<button
				aria-label={`Reload ${ee.name}`}
				class={cn(
					" icon-btn-sm text-white",
					deletable
						? "bg-blue-600"
						: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
				)}
				onclick={() => {
					if (deletable) controller.reload(ee.name);
				}}>
				<FolderSync />
			</button>

			<button
				aria-label={`Remove ${ee.name}`}
				class={cn(
					" icon-btn-sm text-white",
					deletable
						? "bg-red-600"
						: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
				)}
				onclick={() => {
					if (deletable) controller.remove([ee.name]);
				}}>
				<Trash2 />
			</button>
		</div>
	</div>
	<div>
		<div
			class={cn(
				"grid grid-cols-2 border-2 border-slate-800 bg-slate-300 rounded-t p-0.5",
				ee.param_opens ? "" : "rounded-b"
			)}>
			<button
				class={cn(
					"frow items-center   pr-4 rounded-tr rounded-tl h-full"
				)}
				onclick={() => {
					ee.param_opens = !ee.param_opens;
				}}>
				<span class="h-3">
					{#if !ee.param_opens}
						<ChevronRight strokeWidth="3px" />
					{:else}
						<ChevronDown strokeWidth="3px" />
					{/if}
				</span>
				<div class=" font-extrabold wrapped px-0">Params</div>
			</button>

			{#if JSON.stringify(ee.params) !== JSON.stringify(ee.temp_params)}
				<div class="frow-1 items-center place-self-end">
					<button
						aria-label="Save params"
						class="bg-slate-500 icon-btn-sm text-white"
						onclick={() => {
							ee.temp_params = deepCopy(ee.params);
						}}>
						<Undo />
					</button>

					<button
						aria-label="Save params"
						class=" bg-green-500 icon-btn-sm text-white"
						onclick={() => {
							controller.updateParams([ee.name]);
						}}>
						<Check />
					</button>
				</div>
			{/if}
		</div>

		{#if ee.param_opens}
			<div
				class="fcol *:border-b-1 *:border-slate-400 border-2 border-t-0 border-slate-800">
				{#each Object.keys(ee.temp_params) as key}
					{#if ee.temp_params[key].type === "composite"}
						<Composite
							label={key}
							bind:open={ee.composite_opens[key]}
							bind:params={ee.temp_params[key].children} />
					{:else}
						<Param label={key} bind:param={ee.temp_params[key]} />
					{/if}
				{/each}
			</div>
		{/if}
	</div>
	{@render children?.()}
</div>
