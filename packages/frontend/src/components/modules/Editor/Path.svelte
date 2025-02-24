<script lang="ts">
	import { autofocus } from "$components/utils.svelte";
	import Cancel from "$icons/Cancel.svelte";
	import Edit from "$icons/Edit.svelte";
	import Tick from "$icons/Tick.svelte";
	import Separator from "./Separator.svelte";

	let {
		path = $bindable(),
		onconfirm,
	}: {
		path: string | undefined;
		onconfirm: (path: string) => void;
	} = $props();

	let temp_path = $state(path);
	let editing = $state(path === undefined);
</script>

<div class="row-2">
	{#if editing}
		<label class="row-2 bg-white wrapped flex-grow">
			<div class="editor-label">Path</div>
			<Separator />
			<input
				type="text"
				class="flex-grow"
				bind:value={temp_path}
				onfocus={autofocus} />
		</label>
		<div class="row-1">
			{#if path !== undefined && path !== ""}
				<button
					class="icon-btn-sm red"
					onclick={() => {
						temp_path = path;
						editing = false;
					}}><Cancel /></button>
			{:else}
				<div class="icon-btn-sm"></div>
			{/if}
			<button
				class="icon-btn-sm green"
				onclick={() => {
					if (temp_path === undefined || temp_path === "") return;

					editing = false;

					if (temp_path === path) return;

					path = temp_path;
					onconfirm(temp_path);
				}}><Tick /></button>
		</div>
	{:else}
		<div class="row-2 bg-white wrapped min-w-0 flex-grow">
			<div class="editor-label">Path</div>
			<div class="w-0.5 bg-slate-200 rounded-full"></div>
			<div class="min-w-0">
				<div class="overflow-x-scroll">{temp_path}</div>
			</div>
		</div>
		<div class="row-1">
			<div class="icon-btn-sm"></div>
			<button
				class="icon-btn-sm slate"
				onclick={() => {
					editing = true;
				}}><Edit /></button>
		</div>
	{/if}
</div>
