<script lang="ts">
	import Plus from "$icons/Plus.svelte";
	import { eeeditor } from "$components/modules/config/editor/ee/EEEditorController.svelte";
	import { tick } from "svelte";
	import { cn } from "$components/utils.svelte";

	import Disk from "$icons/Disk.svelte";
	import FolderQuestion from "$icons/FolderQuestion.svelte";
	import Sign from "$icons/Sign.svelte";

	import { editor } from "$components/modules/config/editor/EditorController.svelte";
	import { dependency_editor } from "$components/modules/config/editor/Dependency/DependencyEditorController.svelte";
	import type { EEType } from "$states/ee.svelte";
	import { capitalise } from "$lib/utils";
	import { workspace } from "$states/workspace.svelte";

	let { eetype }: { eetype: EEType } = $props();

	const capitalised = capitalise(eetype);

	const addHandler = async () => {
		const new_ee = await workspace.getEEs(eetype).instantiate();
		if (!new_ee) return;
		await tick();

		eeeditor.id = new_ee.id;

		editor.mode = "ee";
		eeeditor.mode = eetype;
		dependency_editor.id = undefined;
	};
</script>

<div class="section fcol-2 bg-slate-200">
	<div class="frow justify-between items-center">
		<div class="title bg-white wrapped">{capitalised}</div>

		<button class="icon-btn-sm slate" onclick={addHandler}><Plus /></button>
	</div>
	{#each Object.values(workspace.getEEsList(eetype)) as e}
		<button
			class={cn(
				"section text-start bg-white frow justify-between items-center ",
				e.id === eeeditor.id
					? "outline outline-offset-2 outline-slate-600"
					: ""
			)}
			onclick={() => {
				editor.mode = "ee";
				dependency_editor.id = undefined;
				eeeditor.id = e.id;
				eeeditor.mode = eetype;
			}}
			id={`${eetype}-${e.id}`}>
			{#if "name" in e && e.name !== ""}
				<div>
					{e.name}
				</div>
			{:else}
				<div class="italic text-slate-500/75">Setup {capitalised}</div>
			{/if}
			<div class="frow-1 flex-row-reverse">
				{#if !e.created}
					<div class="icon-btn-sm border border-red-500 text-red-500">
						<FolderQuestion />
					</div>
				{:else}
					{#if e.name === undefined || e.name === ""}
						<div
							class="icon-btn-sm border border-red-500 text-red-500">
							<Sign />
						</div>
					{/if}
					{#if e.params_edited}
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
