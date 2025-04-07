<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Plus from "$icons/Plus.svelte";
	import { getRandomId } from "$lib/utils";
	import { gstore } from "$states/global.svelte";
	import { tick } from "svelte";
	import { dependency_editor } from "../editor/Dependency/DependencyEditorController.svelte";
	import { editor } from "../editor/EditorController.svelte";
	import ExclamationMark from "$icons/ExclamationMark.svelte";

	import { eeeditor } from "../editor/ee/EEEditorController.svelte";

	const addHandler = async () => {
		const new_dependency =
			await gstore.workspace.dependencies.instantiate();

		await tick();

		editor.mode = "dependency";
		eeeditor.id = undefined;
		dependency_editor.id = new_dependency.id;
	};
</script>

<div class="section fcol-2 bg-slate-200">
	<div class="fcol-2">
		<div class="frow justify-between items-center">
			<div class="title bg-white wrapped self-start">Dependencies</div>
			<div class="frow-1">
				<!-- <button
					class="icon-btn-sm slate"
					onclick={}><Reload /></button
				> -->
				<button class="icon-btn-sm slate" onclick={addHandler}
					><Plus /></button>
			</div>
		</div>

		{#each Object.values(gstore.workspace.dependencies.dependencies) as dependency}
			<button
				class={cn(
					"section text-start bg-white frow justify-between items-center ",
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
				{#if dependency.installed}
					<div>
						{dependency.name}
					</div>
				{:else}
					<div class="italic text-slate-500/75">Setup Dependency</div>
				{/if}
				<div class="frow-1 flex-row-reverse">
					{#if !dependency.installed}
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
