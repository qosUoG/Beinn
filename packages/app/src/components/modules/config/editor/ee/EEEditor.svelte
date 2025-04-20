<script lang="ts">
	import Trash from "$icons/Trash.svelte";

	import { eeeditor } from "./EEEditorController.svelte";
	import Params from "./Params.svelte";
	import EEPath from "./EEPath.svelte";
	import Cancel from "$icons/Cancel.svelte";

	import Disk from "$icons/Disk.svelte";
	import FixedField from "$components/reuseables/Fields/FixedField.svelte";
	import LabelField from "$components/reuseables/Fields/LabelField.svelte";
	import { autofocus } from "$components/utils.svelte";

	import { capitalise } from "$lib/utils";
	import { workspace } from "$states/workspace.svelte";

	const removeHandler = async () => {
		await target.remove();
		eeeditor.id = undefined;
	};

	const createHandler = async () => {
		await target.create();
	};

	const saveParamsHandler = async () => {
		await target.saveParams();
	};

	const target = $derived(workspace.getEE(eeeditor.mode, eeeditor.id!));
</script>

{#if eeeditor.id !== undefined && target}
	{#key eeeditor.id}
		<div class="section bg-slate-200 col-span-2 min-w-0 w-full">
			<div class="fcol-2 min-w-0 w-full">
				<div class="frow justify-between items-end">
					<div class="title bg-white wrapped">
						Editor - {capitalise(eeeditor.mode)}
					</div>
					<button class="icon-btn-sm red" onclick={removeHandler}
						><Trash /></button>
				</div>

				<EEPath
					ee={target}
					options={workspace.getEEs(eeeditor.mode)
						.available_module_cls}
					onconfirm={createHandler} />

				{#if target.created}
					<div class="frow justify-between mt-4 items-end">
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

					<div class="frow justify-between mt-4 items-end">
						<div class="title bg-white wrapped">Parameters</div>
						<div class="frow-1">
							{#if target.params_edited}
								<button
									class="icon-btn-sm red"
									onclick={() => {
										target.cancelTempParams();
									}}><Cancel /></button>
								<button
									class="icon-btn-sm green"
									onclick={saveParamsHandler}
									><Disk /></button>
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
		</div>
	{/key}
{/if}
