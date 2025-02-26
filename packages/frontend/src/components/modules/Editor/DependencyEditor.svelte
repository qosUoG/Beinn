<script lang="ts">
	import Trash from "$icons/Trash.svelte";
	import { gstore } from "$states/global.svelte";
	import type { Dependency } from "qoslab-shared";

	import { dependency_editor } from "./DependencyEditorController.svelte";

	import Separator from "./Separator.svelte";
	import { autofocus } from "$components/utils.svelte";
	import Download from "$icons/Download.svelte";

	const dependency: Dependency | undefined = $derived.by(() => {
		if (dependency_editor.id === undefined) return undefined;
		$inspect(gstore.workspace.dependencies[dependency_editor.id].source);
		return gstore.workspace.dependencies[dependency_editor.id];
	});

	let temp_source = $state("");
</script>

{#key dependency_editor.id}
	<div class="container bg-slate-200 col-span-2">
		{#if dependency !== undefined}
			<div class="col-2">
				<div class="row justify-between items-end">
					<div class="title bg-white wrapped">
						Editor - Dependency
					</div>
					<Bin />
				</div>

				<div class="row-2">
					{#if !dependency.confirmed}
						<label class="row-2 bg-white wrapped flex-grow">
							<div class="editor-label">Source</div>
							<Separator />
							<input
								type="text"
								class="flex-grow"
								bind:value={temp_source}
								onfocus={autofocus} />
						</label>

						<button
							class="icon-btn-sm green"
							onclick={() => {
								if (
									temp_source === undefined ||
									temp_source === ""
								)
									return;
								// TODO
								dependency.confirmed = true;
							}}><Download /></button>
					{:else if dependency.source.type === "pip"}
						<div class="row-2 bg-white wrapped flex-grow">
							<div class="editor-label">Package</div>
							<Separator />
							<div class="flex-grow">
								{dependency.name}
							</div>
						</div>
					{:else if dependency.source.type === "git"}
						<div class="row-2 bg-white wrapped flex-grow">
							<div class="editor-label">Git Path</div>
							<Separator />
							<div class="flex-grow">
								{dependency.source.git}
								{dependency.source.subdirectory}
							</div>
						</div>
					{:else if dependency.source.type === "path"}
						<div class="row-2 bg-white wrapped flex-grow">
							<div class="editor-label">Path</div>
							<Separator />
							<div class="flex-grow">
								{dependency.source.path}
							</div>
						</div>
					{/if}
				</div>
			</div>
		{/if}
	</div>
{/key}

{#snippet Bin()}
	<button
		class="icon-btn-sm red"
		onclick={() => {
			// TODO remove dependency in python project

			delete gstore.workspace.dependencies[dependency_editor.id!];

			dependency_editor.id = undefined;
		}}><Trash /></button>
{/snippet}
