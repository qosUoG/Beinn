<script lang="ts">
	import Plus from "$icons/Plus.svelte";

	import { getRandomId } from "$lib/utils";
	import { gstore } from "$states/global.svelte";
	import { eeeditor } from "$components/modules/config/editor/ee/EEEditorController.svelte";
	import { tick } from "svelte";
	import { cn } from "$components/utils.svelte";

	import Disk from "$icons/Disk.svelte";
	import FolderQuestion from "$icons/FolderQuestion.svelte";
	import Sign from "$icons/Sign.svelte";

	import { getAvailableEEs } from "$services/qoslabapp.svelte";
	import { editor } from "$components/modules/config/editor/EditorController.svelte";
	import { dependency_editor } from "$components/modules/config/editor/Dependency/DependencyEditorController.svelte";
	import { capitalise } from "qoslab-shared";

	let { eetype }: { eetype: "equipment" | "experiment" } = $props();

	const capitalised = capitalise(eetype);
</script>

<div class="section col-2 bg-slate-200">
	<div class="row justify-between items-center">
		<div class="title bg-white wrapped">
			{capitalised}
		</div>

		<button
			class="icon-btn-sm slate"
			onclick={async () => {
				const id = getRandomId(Object.keys(gstore[`${eetype}s`]));
				gstore[`${eetype}s`][id] = {
					id,
					created: false,
					module_cls: { module: "", cls: "" },
				};

				gstore.workspace[`available_${eetype}s`] =
					await getAvailableEEs(eetype);

				await tick();
				editor.mode = "ee";
				eeeditor.id = id;
				eeeditor.mode = eetype;
				dependency_editor.id = undefined;
			}}><Plus /></button>
	</div>
	{#each Object.values(gstore[`${eetype}s`]) as target}
		{@const params_edited = target.created
			? JSON.stringify(target.temp_params) !==
				JSON.stringify(target.params)
			: false}
		<button
			class={cn(
				"section text-start bg-white row justify-between items-center ",
				target.id === eeeditor.id
					? "outline outline-offset-2 outline-slate-600"
					: ""
			)}
			onclick={() => {
				editor.mode = "ee";
				dependency_editor.id = undefined;
				eeeditor.id = target.id;
				eeeditor.mode = eetype;
			}}
			id={`equipment-${target.id}`}>
			{#if "name" in target && target.name !== ""}
				<div>
					{target.name}
				</div>
			{:else}
				<div class="italic text-slate-500/75">Setup {capitalised}</div>
			{/if}
			<div class="row-1 flex-row-reverse">
				{#if !target.created}
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
