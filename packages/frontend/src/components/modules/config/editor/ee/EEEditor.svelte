<script lang="ts">
	import Trash from "$icons/Trash.svelte";
	import {
		createEE,
		getEEParams,
		removeEE,
		setEEParams,
		subscribeExperimentEventsWs,
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
	import { capitalise } from "qoslab-shared";
	import {
		getExperimentEventFn,
		type CreatedRuntimeExperiment,
	} from "$states/experiment";

	let target = $derived.by(() => {
		if (eeeditor.id === undefined) return undefined;

		return gstore[`${eeeditor.mode}s`][eeeditor.id];
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
	<div class="section bg-slate-200 col-span-2 min-w-0 w-full">
		{#if eeeditor.id !== undefined && target !== undefined}
			<div class="col-2 min-w-0 w-full">
				<div class="row justify-between items-end">
					<div class="title bg-white wrapped">
						Editor - {capitalise(eeeditor.mode)}
					</div>
					<button
						class="icon-btn-sm red"
						onclick={async () => {
							if (eeeditor.id === undefined)
								throw Error(
									"ERROR: eeeditor.id shall not be undeifned"
								);

							await removeEE(eeeditor.mode, { id: eeeditor.id });
							delete gstore[`${eeeditor.mode}s`][eeeditor.id];
							eeeditor.id = undefined;
						}}><Trash /></button>
				</div>

				<EEPath
					bind:value={target.module_cls}
					options={gstore.workspace[`available_${eeeditor.mode!}s`]}
					created={target.created}
					onconfirm={async () => {
						// Pleasing the type checker
						if (target === undefined || eeeditor.id === undefined)
							return;
						// Create the equipment / experiment
						await createEE(eeeditor.mode, target);

						await tick();

						// Fetch the params
						const params = await getEEParams(eeeditor.mode, target);

						if (eeeditor.mode === "equipment")
							gstore.equipments[eeeditor.id] = {
								...target,
								created: true,
								params: { ...params },
								temp_params: { ...params },
								name: "",
							};
						else if (eeeditor.mode === "experiment") {
							gstore.experiments[eeeditor.id] = {
								...target,
								created: true,
								params: { ...params },
								temp_params: { ...params },
								name: "",
								chart_configs: {},
								status: "initial",
								iteration_count: -1,
								iteration_time_start: 0,
								total_time: 0,
							};

							await tick();

							// Start listening to experiment events here
							subscribeExperimentEventsWs({
								id: target.id,
								onmessage: getExperimentEventFn(
									gstore.experiments[
										eeeditor.id
									] as CreatedRuntimeExperiment
								),
							});
						}
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
										await setEEParams(
											eeeditor.mode,
											target
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
