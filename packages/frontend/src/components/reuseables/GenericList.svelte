<script lang="ts" generics="T extends Equipment | Experiment">
	import Plus from "$icons/Plus.svelte";

	import { getRandomId } from "$lib/utils";
	import { gstore } from "$states/global.svelte";
	import { editor } from "$components/modules/Editor/EditorController.svelte";
	import { tick } from "svelte";
	import { cn } from "$components/utils.svelte";

	import Disk from "$icons/Disk.svelte";
	import FolderQuestion from "$icons/FolderQuestion.svelte";
	import Sign from "$icons/Sign.svelte";
	import Usb from "$icons/USB.svelte";
	import { loadEquipment } from "$services/backend.svelte";
	import type { Equipment, Experiment } from "$states/types/general";
</script>

<div class="container col-2 bg-slate-200">
	<div class="row justify-between items-center">
		<div class="title">Equipment</div>
		<div class="row-1">
			<button class="icon-btn-sm green" onclick={loadEquipment}>
				<Usb />
			</button>
			<button
				class="icon-btn-sm slate"
				onclick={async () => {
					const id = getRandomId(Object.keys(gstore.equipments));
					gstore.equipments[id] = { id };

					await tick();

					editor.id = id;
					editor.mode = "Equipment";
				}}><Plus /></button>
		</div>
	</div>
	{#each Object.values(gstore.equipments) as equipment}
		{@const params_edited =
			JSON.stringify(equipment!.temp_params) !==
			JSON.stringify(equipment!.params)}
		<button
			class={cn(
				"container text-start bg-white row justify-between items-center ",
				equipment.id === editor.id
					? "outline outline-offset-2 outline-slate-600"
					: ""
			)}
			onclick={() => {
				editor.id = equipment.id;
				editor.mode = "Equipment";
			}}
			id={`equipment-${equipment.id}`}>
			{#if equipment.name !== undefined && equipment.name !== ""}
				<div>
					{equipment.name}
				</div>
			{:else}
				<div class="italic text-slate-500/75">Setup Equipment</div>
			{/if}
			<div class="row-1 flex-row-reverse">
				{#if equipment.path === undefined}
					<div class="icon-btn-sm border border-red-500 text-red-500">
						<FolderQuestion />
					</div>
				{:else}
					{#if equipment.name === undefined || equipment.name === ""}
						<div
							class="icon-btn-sm border border-red-500 text-red-500">
							<Sign />
						</div>
					{/if}
					{#if params_edited}
						<div
							class="icon-btn-sm border border-red-500 text-red-500">
							<Disk />
						</div>
					{/if}

					<div class="h-6"></div>
				{/if}
			</div>
		</button>
	{/each}
</div>
