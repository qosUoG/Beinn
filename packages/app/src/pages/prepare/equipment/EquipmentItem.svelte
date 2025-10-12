<script lang="ts">
	import {
		equipment_controller,
		type Equipment,
	} from "$controllers/equipment.svelte";

	let { equipment = $bindable() }: { equipment: Equipment } = $props();

	import {
		ChevronDown,
		ChevronRight,
		FolderSync,
		Trash2,
	} from "@lucide/svelte";
	import Param from "../_ee/Param.svelte";
	import Composite from "../_ee/Composite.svelte";

	import { cn } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
</script>

<div class="bg-white rounded fcol-1 p-1">
	<div class="flex items-center w-full justify-between">
		{#if experiment_controller.closeable}
			<input
				class="  font-light text-slate-950 flex items-center px-1 text-sm"
				bind:value={equipment.name} />
		{:else}<div
				class="  font-light text-slate-950 flex items-center px-1 text-sm">
				{equipment.name}
			</div>
		{/if}

		<div class="frow-1">
			<button
				aria-label={`Reload ${equipment.name}`}
				class={cn(
					" icon-btn-sm text-white ",
					experiment_controller.closeable
						? "bg-blue-600"
						: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
				)}
				onclick={() => {
					if (experiment_controller.closeable)
						equipment_controller.reload(equipment.name);
				}}>
				<FolderSync />
			</button>

			<button
				aria-label={`Remove ${equipment.name}`}
				class={cn(
					" icon-btn-sm text-white ",
					experiment_controller.closeable
						? "bg-red-600"
						: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
				)}
				onclick={() => {
					if (experiment_controller.closeable)
						equipment_controller.remove(equipment.name);
				}}>
				<Trash2 />
			</button>
		</div>
	</div>
	<div>
		<div
			class={cn(
				"grid grid-cols-2 border-2 border-slate-800 bg-slate-300 rounded-t p-0.5",
				equipment.param_opens ? "" : "rounded-b"
			)}>
			<button
				class={cn(
					"frow items-center   pr-4 rounded-tr rounded-tl h-full"
				)}
				onclick={() => {
					equipment.param_opens = !equipment.param_opens;
				}}>
				<span class="h-3">
					{#if !equipment.param_opens}
						<ChevronRight strokeWidth="3px" />
					{:else}
						<ChevronDown strokeWidth="3px" />
					{/if}
				</span>
				<div class="  wrapped px-0">Params</div>
			</button>
		</div>

		{#if equipment.param_opens}
			<div
				class="fcol *:border-b-1 *:border-slate-400 border-2 border-t-0 border-slate-800">
				{#each Object.keys(equipment.params) as key}
					{#if equipment.params[key].type === "composite"}
						<Composite
							label={key}
							bind:open={equipment.composite_opens[key]}
							bind:params={equipment.params[key].children} />
					{:else}
						<Param label={key} bind:param={equipment.params[key]} />
					{/if}
				{/each}
			</div>
		{/if}
	</div>
</div>
