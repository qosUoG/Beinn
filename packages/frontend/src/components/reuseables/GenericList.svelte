<script lang="ts">
	import Plus from "$icons/Plus.svelte";

	import { getRandomId } from "$lib/utils";
	import { gstore } from "$states/global.svelte";
	import { eeeditor } from "$components/modules/Editor/EEEditorController.svelte";
	import { tick } from "svelte";
	import { cn } from "$components/utils.svelte";

	import Disk from "$icons/Disk.svelte";
	import FolderQuestion from "$icons/FolderQuestion.svelte";
	import Sign from "$icons/Sign.svelte";

	import {
		getAvailableEquipments,
		getAvailableExperiments,
	} from "$services/qoslabapp.svelte";
	import { editor } from "$components/modules/Editor/EditorController.svelte";
	import { dependency_editor } from "$components/modules/Editor/DependencyEditorController.svelte";

	let { listtype }: { listtype: "equipments" | "experiments" } = $props();

	const capitalised = listtype[0].toUpperCase() + String(listtype).slice(1);
</script>

<div class="container col-2 bg-slate-200">
	<div class="row justify-between items-center">
		<div class="title bg-white wrapped">
			{capitalised}
		</div>

		<button
			class="icon-btn-sm slate"
			onclick={async () => {
				const id = getRandomId(Object.keys(gstore[listtype]));
				gstore[listtype][id] = { id };

				if (listtype === "equipments")
					gstore.workspace.available_equipments =
						await getAvailableEquipments();
				else if (listtype === "experiments")
					gstore.workspace.available_experiments =
						await getAvailableExperiments();

				await tick();
				editor.mode = "ee";
				eeeditor.id = id;
				eeeditor.mode = listtype;
				dependency_editor.id = undefined;
			}}><Plus /></button>
	</div>
	{#each Object.values(gstore[listtype]) as target}
		{@const params_edited =
			JSON.stringify(target.temp_params) !==
			JSON.stringify(target.params)}
		<button
			class={cn(
				"container text-start bg-white row justify-between items-center ",
				target.id === eeeditor.id
					? "outline outline-offset-2 outline-slate-600"
					: ""
			)}
			onclick={() => {
				editor.mode = "ee";
				dependency_editor.id = undefined;
				eeeditor.id = target.id;
				eeeditor.mode = listtype;
			}}
			id={`equipment-${target.id}`}>
			{#if target.name !== undefined && target.name !== ""}
				<div>
					{target.name}
				</div>
			{:else}
				<div class="italic text-slate-500/75">Setup {capitalised}</div>
			{/if}
			<div class="row-1 flex-row-reverse">
				{#if target.module === undefined}
					<div class="icon-btn-sm border border-red-500 text-red-500">
						<FolderQuestion />
					</div>
				{:else}
					{#if target.name === undefined || target.name === ""}
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
