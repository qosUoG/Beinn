<script lang="ts">
	import Trash from "$icons/Trash.svelte";
	import { getEquipmentParams } from "$services/qoslabapp.svelte";
	import { gstore } from "$states/global.svelte";
	import type { Equipment, Experiment } from "qoslab-shared";
	import { tick } from "svelte";
	import { eeeditor } from "./EEEditorController.svelte";
	import Name from "./Name.svelte";
	import Params from "./Params.svelte";
	import Path from "./EEPath.svelte";
	import Cancel from "$icons/Cancel.svelte";

	import Disk from "$icons/Disk.svelte";

	const target: Experiment | Equipment | undefined = $derived.by(() => {
		if (eeeditor.id === undefined) return undefined;

		if (eeeditor.mode === "equipments")
			return gstore.equipments[eeeditor.id];

		if (eeeditor.mode === "experiments")
			return gstore.experiments[eeeditor.id];
	});

	let params_edited = $derived.by(() => {
		return (
			JSON.stringify(target!.temp_params) !==
			JSON.stringify(target!.params)
		);
	});
</script>

{#key eeeditor.id}
	<div class="container bg-slate-200 col-span-2">
		{#if eeeditor.id !== undefined}
			<div class="col-2">
				<div class="row justify-between items-end">
					<div class="title bg-white wrapped">
						Editor -
						{#if eeeditor.mode === "equipments"}
							Equipment
						{:else if eeeditor.mode === "experiments"}
							Experiment
						{/if}
					</div>
					<Bin />
				</div>

				<Path
					bind:path={target!.path}
					onconfirm={async (path: string) => {
						target!.params = await getEquipmentParams(path);
						await tick();
						target!.temp_params = JSON.parse(
							JSON.stringify(target!.params)
						);
					}} />

				{#if target!.path}
					<Name bind:name={target!.name} />
				{/if}
				{#if target!.temp_params}
					<div class="row justify-between mt-4 items-end">
						<div class="title">Parameters</div>
						<div class="row-1">
							{#if params_edited}
								<button
									class="icon-btn-sm red"
									onclick={() => {
										target!.temp_params = JSON.parse(
											JSON.stringify(target!.params)
										);
									}}><Cancel /></button>
								<button
									class="icon-btn-sm green"
									onclick={() => {
										target!.params = JSON.parse(
											JSON.stringify(target!.temp_params)
										);
									}}><Disk /></button>
							{:else}
								<div class="h-6"></div>
							{/if}
						</div>
					</div>
					<div class="grid grid-cols-2 gap-2">
						<Params bind:params={target!.temp_params} />
					</div>
				{/if}
			</div>
		{/if}
	</div>
{/key}

{#snippet Bin()}
	<button
		class="icon-btn-sm red"
		onclick={() => {
			switch (eeeditor.mode) {
				case "equipments":
					delete gstore.equipments[eeeditor.id!];
					break;
				case "experiments":
					delete gstore.experiments[eeeditor.id!];
			}

			eeeditor.id = undefined;
		}}><Trash /></button>
{/snippet}
