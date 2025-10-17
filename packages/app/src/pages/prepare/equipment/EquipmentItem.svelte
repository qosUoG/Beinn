<script lang="ts">
	import { equipment_controller } from "$controllers/equipment.svelte";

	let { equipment = $bindable() }: { equipment: Instance } = $props();

	import {
		ChevronDown,
		ChevronRight,
		FolderSync,
		LoaderCircle,
		Trash2,
	} from "@lucide/svelte";
	import Param from "../_ee/Param.svelte";
	import Composite from "../_ee/Composite.svelte";

	import { cn } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import ParamList from "../_ee/ParamList.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import type { Instance } from "$controllers/_ee.svelte";
</script>

<div class="bg-white rounded fcol-1 p-1">
	<div class="flex items-center w-full justify-between">
		{#if experiment_controller.editable}
			<input
				class="  font-light text-slate-950 flex items-center px-1 text-sm"
				bind:value={
					() => equipment.name,
					(v: string) => {
						equipment.name = v;
						equipment_controller.save();
					}
				} />
		{:else}<div
				class="  font-light text-slate-950 flex items-center px-1 text-sm">
				{equipment.name}
			</div>
		{/if}

		<div class="frow-1">
			{#if equipment.reloading}
				<div class="icon-btn-sm bg-blue-600">
					<div class="text-white animate-spin">
						<LoaderCircle />
					</div>
				</div>
			{:else}
				<button
					aria-label={`Reload ${equipment.name}`}
					class={cn(
						" icon-btn-sm text-white ",
						experiment_controller.editable
							? "bg-blue-600"
							: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
					)}
					onclick={() => {
						if (experiment_controller.editable) equipment.reload();
					}}>
					<FolderSync />
				</button>{/if}

			<button
				aria-label={`Remove ${equipment.name}`}
				class={cn(
					" icon-btn-sm text-white ",
					experiment_controller.editable
						? "bg-red-600"
						: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
				)}
				onclick={() => {
					if (experiment_controller.editable)
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

		<ParamList
			param_opens={equipment.param_opens}
			bind:composite_opens={equipment.composite_opens}
			bind:params={equipment.params}
			saveFn={async () => {
				await equipment_controller.save();
			}} />
	</div>
</div>
