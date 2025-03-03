<script lang="ts">
	import Trash from "$icons/Trash.svelte";
	import { gstore } from "$states/global.svelte";
	import type { Dependency } from "qoslab-shared";

	import { dependency_editor } from "./DependencyEditorController.svelte";

	import Separator from "./Separator.svelte";
	import { autofocus } from "$components/utils.svelte";
	import Download from "$icons/Download.svelte";
	import {
		addDependency,
		readDependency,
		removeDependency,
	} from "$services/backend.svelte";

	const dependency: Dependency | undefined = $derived.by(() => {
		if (dependency_editor.id === undefined) return undefined;

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
					{@render Bin()}
				</div>

				{#if !dependency.confirmed}
					<div class="row-2 w-full">
						<label class="row-2 bg-white wrapped w-full flex-grow">
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
							onclick={async () => {
								if (
									temp_source === undefined ||
									temp_source === ""
								)
									return;

								await addDependency(temp_source);

								const current_dependencies = $state.snapshot(
									gstore.workspace.dependencies
								);
								temp_source = "";

								const res = await readDependency();

								gstore.workspace.dependencies = res;

								dependency_editor.id = Object.values(res).find(
									(d) =>
										Object.values(
											current_dependencies
										).find((dd) => d.name === dd.name) ===
										undefined
								)!.id;
							}}><Download /></button>
					</div>
				{:else if dependency.source.type === "pip"}
					<div class="row-2 bg-white wrapped w-full">
						<div class="editor-label">Package</div>
						<Separator />
						<div class="">
							{dependency.fullname}
						</div>
					</div>
				{:else if dependency.source.type === "git"}
					<div class="row-2 bg-white wrapped w-full">
						<div class="editor-label">Git Path</div>
						<Separator />
						<div class="">
							{dependency.source.git}
						</div>
					</div>
					{#if dependency.source.subdirectory}
						<div class="row-2 bg-white wrapped w-full">
							<div class="editor-label">Subdirectory</div>
							<Separator />
							<div class="">
								{dependency.source.subdirectory}
							</div>
						</div>
					{/if}
				{:else if dependency.source.type === "path"}
					<div class="row-2 bg-white wrapped w-full">
						<div class="editor-label">Path</div>
						<Separator />
						<div class="">
							{dependency.source.path}
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>
{/key}

{#snippet Bin()}
	<button
		class="icon-btn-sm red"
		onclick={async () => {
			console.log(dependency);
			if (dependency?.confirmed)
				// TODO remove dependency in python project
				await removeDependency(dependency.name!);

			delete gstore.workspace.dependencies[dependency_editor.id!];

			dependency_editor.id = undefined;
		}}><Trash /></button>
{/snippet}
