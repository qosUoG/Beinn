<script lang="ts">
	import Trash from "$icons/Trash.svelte";
	import {
		getEquipmentParams,
		getExperimentParams,
		setEquipmentParams,
		setExperimentParams,
	} from "$services/qoslabapp.svelte";
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
	<div class="container bg-slate-200 col-span-2 min-w-0 w-full">
		{#if eeeditor.id !== undefined}
			<div class="col-2 min-w-0 w-full">
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
					bind:module={target!.module}
					bind:cls={target!.cls}
					options={gstore.workspace[
						`available_${eeeditor.mode!}`
					].map(({ modules, cls }) => `${modules[0]} ${cls}`)}
					onconfirm={async (path) => {
						if (eeeditor.mode === "equipments")
							target!.params = await getEquipmentParams(path);
						else if (eeeditor.mode === "experiments")
							target!.params = await getExperimentParams(path);
						await tick();
						target!.temp_params = JSON.parse(
							JSON.stringify(target!.params)
						);
					}} />

				{#if target!.module && target!.cls}
					<Name bind:name={target!.name} />
				{/if}
				{#if target!.temp_params && target!.name}
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
									onclick={async () => {
										target!.params = JSON.parse(
											JSON.stringify(target!.temp_params)
										);
										await tick();
										if (eeeditor.mode === "equipments")
											await setEquipmentParams(
												target!.name!,
												target!.params!
											);
										else if (
											eeeditor.mode === "experiments"
										)
											await setExperimentParams(
												target!.name!,
												target!.params!
											);
									}}><Disk /></button>
							{:else}
								<div class="h-6"></div>
							{/if}
						</div>
					</div>
					<div class="grid grid-cols-2 gap-2 min-w-0 w-full">
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
