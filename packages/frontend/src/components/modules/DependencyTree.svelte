<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Plus from "$icons/Plus.svelte";
	import { getRandomId } from "$lib/utils";
	import { gstore } from "$states/global.svelte";
	import { tick } from "svelte";
	import { dependency_editor } from "./Editor/DependencyEditorController.svelte";
	import { editor } from "./Editor/EditorController.svelte";
	import ExclamationMark from "$icons/ExclamationMark.svelte";
	import Reload from "$icons/Reload.svelte";
	import { readDependency } from "$services/backend.svelte";
	import { eeeditor } from "./Editor/EEEditorController.svelte";
</script>

<div class="container col-2 bg-slate-200">
	<div class="col-2">
		<div class="row justify-between items-center">
			<div class="title bg-white wrapped self-start">Dependencies</div>
			<div class="row-1">
				<button
					class="icon-btn-sm slate"
					onclick={async (e) => {
						gstore.workspace.dependencies = await readDependency();
					}}><Reload /></button>
				<button
					class="icon-btn-sm slate"
					onclick={async (e) => {
						const id = getRandomId(
							Object.keys(gstore.workspace.dependencies)
						);
						gstore.workspace.dependencies[id] = {
							id,
							confirmed: false,
							source: {
								type: "pip",
							},
						};

						await tick();

						editor.mode = "dependency";
						dependency_editor.id = id;
					}}><Plus /></button>
			</div>
		</div>

		{#each Object.values(gstore.workspace.dependencies) as dependency}
			<button
				class={cn(
					"container text-start bg-white row justify-between items-center ",
					dependency.id === dependency_editor.id
						? "outline outline-offset-2 outline-slate-600"
						: ""
				)}
				onclick={() => {
					editor.mode = "dependency";
					dependency_editor.id = dependency.id;
					eeeditor.id = undefined;
				}}
				id={`equipment-${dependency.id}`}>
				{#if dependency.name !== undefined && dependency.name !== ""}
					<div>
						{dependency.name}
					</div>
				{:else}
					<div class="italic text-slate-500/75">Setup Dependency</div>
				{/if}
				<div class="row-1 flex-row-reverse">
					{#if !dependency.confirmed}
						<div
							class="icon-btn-sm border border-red-500 text-red-500">
							<ExclamationMark />
						</div>
					{:else}
						<div class="h-6"></div>
					{/if}
				</div>
			</button>
		{/each}
	</div>
</div>
