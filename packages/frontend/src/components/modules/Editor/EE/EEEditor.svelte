<script lang="ts">
	import Trash from "$icons/Trash.svelte";
	import {
		createEquipment,
		createExperiment,
		getEquipmentParams,
		setEquipmentParams,
		setExperimentParams,
	} from "$services/qoslabapp.svelte";
	import { gstore } from "$states/global.svelte";

	import { tick } from "svelte";
	import { eeeditor } from "./EEEditorController.svelte";
	import Params from "./Params.svelte";
	import EEPath from "./EEPath.svelte";
	import Cancel from "$icons/Cancel.svelte";

	import Disk from "$icons/Disk.svelte";
	import FixedField from "$components/reuseables/Fields/FixedField.svelte";
	import LabelField from "$components/reuseables/Fields/LabelField.svelte";
	import { autofocus } from "$components/utils.svelte";

	let target = $derived.by(() => {
		if (eeeditor.id === undefined) return undefined;

		if (eeeditor.mode === "equipments")
			return gstore.equipments[eeeditor.id];

		if (eeeditor.mode === "experiments")
			return gstore.experiments[eeeditor.id];
	});

	let params_edited = $derived.by(() => {
		if (!target?.created) return false;

		return (
			JSON.stringify(target!.temp_params) !==
			JSON.stringify(target!.params)
		);
	});
</script>

{#key eeeditor.id}
	<div class="container bg-slate-200 col-span-2 min-w-0 w-full">
		{#if eeeditor.id !== undefined && target !== undefined}
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

				<EEPath
					bind:value={target.module_cls}
					options={gstore.workspace[`available_${eeeditor.mode!}`]}
					created={target.created}
					onconfirm={async () => {
						// Pleasing the type checker
						if (target === undefined || eeeditor.id === undefined)
							return;
						// Create the equipment / experiment
						if (eeeditor.mode === "equipments")
							await createEquipment(target.id, target.module_cls);
						else if (eeeditor.mode === "experiments")
							await createExperiment(
								target.id,
								target.module_cls
							);

						await tick();

						// Fetch the params
						const params = await getEquipmentParams(target.id);
						gstore[eeeditor.mode][eeeditor.id] = {
							...target,
							created: true,
							params: { ...params },
							temp_params: { ...params },
							name: "",
						};
					}} />

				{#if target.created}
					<div class="row justify-between mt-4 items-end">
						<div class="title bg-white wrapped">Instance</div>
					</div>
					<FixedField key="id" value={target.id} />
					<LabelField key="Name">
						<input
							type="text"
							class="w-full"
							onkeydown={(e: KeyboardEvent) => {
								if (e.key === "Backspace" || e.key === "Delete")
									return;
								if (/[A-Za-z0-9_\- ]/.test(e.key)) return;

								e.preventDefault();
							}}
							bind:value={target.name}
							onfocus={autofocus} />
					</LabelField>

					<div class="row justify-between mt-4 items-end">
						<div class="title bg-white wrapped">Parameters</div>
						<div class="row-1">
							{#if params_edited}
								<button
									class="icon-btn-sm red"
									onclick={() => {
										target.temp_params = JSON.parse(
											JSON.stringify(target.params)
										);
									}}><Cancel /></button>
								<button
									class="icon-btn-sm green"
									onclick={async () => {
										target.params = JSON.parse(
											JSON.stringify(target.temp_params)
										);
										await tick();
										if (eeeditor.mode === "equipments")
											await setEquipmentParams(
												target.name!,
												target.params!
											);
										else if (
											eeeditor.mode === "experiments"
										)
											await setExperimentParams(
												target.name!,
												target.params!
											);
									}}><Disk /></button>
							{:else}
								<div class="h-6"></div>
							{/if}
						</div>
					</div>
					<div class="grid grid-cols-2 gap-2 min-w-0 w-full">
						<Params bind:params={target.temp_params} />
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
