<script lang="ts">
	import Trash from "$icons/Trash.svelte";
	import { getEquipmentParams } from "$services/backend.svelte";
	import { gstore } from "$states/global.svelte";
	import type { Equipment, Experiment } from "$states/types/general";
	import { tick } from "svelte";
	import { editor } from "./EditorController.svelte";
	import Name from "./Name.svelte";
	import Params from "./Params.svelte";
	import Path from "./Path.svelte";
	import Cancel from "$icons/Cancel.svelte";
	import Tick from "$icons/Tick.svelte";
	import Disk from "$icons/Disk.svelte";

	const target: Experiment | Equipment | undefined = $derived.by(() => {
		if (editor.id === undefined) return undefined;

		if (editor.mode === "Equipment") return gstore.equipments[editor.id];

		if (editor.mode === "Experiment") return gstore.experiments[editor.id];
	});

	let params_edited = $derived.by(() => {
		return (
			JSON.stringify(target!.temp_params) !==
			JSON.stringify(target!.params)
		);
	});
</script>

{#key editor.id}
	<div class="container bg-slate-200 col-span-2">
		{#if editor.id !== undefined}
			<div class="col-2">
				<div class="row justify-between items-end">
					<div class="title">
						Editor -
						{#if editor.mode === "Equipment"}
							Equipment
						{:else if editor.mode === "Experiment"}
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
			switch (editor.mode) {
				case "Equipment":
					delete gstore.equipments[editor.id!];
					break;
				case "Experiment":
					delete gstore.experiments[editor.id!];
			}

			editor.id = undefined;
		}}><Trash /></button>
{/snippet}
