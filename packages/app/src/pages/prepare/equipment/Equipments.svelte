<script lang="ts">
	import { equipment_controller } from "$controllers/equipment.svelte";
	import EquipmentREPL from "./EquipmentREPL.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import EquipmentItem from "./EquipmentItem.svelte";
	import NewEquipment from "./NewEquipment.svelte";
	import { ChevronsLeftRightEllipsis } from "@lucide/svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { cn } from "$components/utils.svelte";
</script>

<div class="justify-between fcol-2 min-h-0 bg-slate-200 rounded p-2">
	<div class="fcol-2 grow min-h-0">
		<div class="frow justify-between items-center">
			<div class="title">Equipment</div>
			{#if workspace_controller.status === "ready"}
				<button
					aria-label={`REPL all`}
					class={cn(
						" icon-btn-sm text-white ",
						experiment_controller.editable
							? " bg-green-500"
							: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
					)}
					onclick={async () => {
						if (experiment_controller.editable)
							await equipment_controller.startREPL(undefined);
					}}>
					<ChevronsLeftRightEllipsis />
				</button>
			{/if}
		</div>
		<div
			class="fcol-2 overflow-y-scroll scrollbar-slate-400 -mr-2 grow pb-8">
			{#if workspace_controller.status === "ready"}
				{#each equipment_controller.equipments as equipment}
					<EquipmentItem bind:equipment />
				{/each}
			{/if}
		</div>
	</div>
	{#if workspace_controller.status === "ready"}
		<NewEquipment />
	{/if}
</div>

{#if equipment_controller.repl}
	<EquipmentREPL />
{/if}
