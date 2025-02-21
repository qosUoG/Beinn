<script lang="ts">
	import Trash from "$icons/Trash.svelte";
	import {
		gstore,
		type Equipment,
		type Experiment,
	} from "$states/global.svelte";
	import { editor } from "./EditorController.svelte";

	const target: Experiment | Equipment | undefined = $derived.by(() => {
		if (editor.id === undefined) return undefined;

		if (editor.mode === "Equipment") return gstore.equipments[editor.id];

		if (editor.mode === "Experiment") return gstore.experiments[editor.id];
	});
</script>

<div class="container bg-slate-200 col-span-2">
	{#if editor.id !== undefined}
		{#if editor.mode === "Equipment"}
			<div class="grid grid-cols-">
				<div class="row justify-between items-center">
					<div class="title">Editor - Equipment</div>
					<Bin />
				</div>

				{#if target!.path === undefined}
					<div class="row-2 items-center">
						<div>Path</div>
						<input type="text" class="wrapped bg-white flex-grow" />
					</div>
				{/if}
			</div>
		{:else if editor.mode === "Experiment"}
			<div class="row justify-between items-center">
				<div class="title">Editor - Experiment</div>
				<Bin />
			</div>
		{/if}
	{/if}
</div>

{#snippet Bin()}
	<button
		class="icon-btn-sm bg-red-200 text-red-800"
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
