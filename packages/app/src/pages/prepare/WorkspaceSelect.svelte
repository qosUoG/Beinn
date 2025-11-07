<script lang="ts">
	import { open } from "@tauri-apps/plugin-dialog";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import { FolderOpen, Keyboard, LoaderCircle } from "@lucide/svelte";

	import { load, type Store } from "@tauri-apps/plugin-store";

	let store: Store;

	async function getSavedWorkspacePath() {
		if (!store) store = await load("workspace_path.json");
		return await store.get<string>("workspace_path");
	}

	import { homeDir } from "@tauri-apps/api/path";

	import { Command } from "@tauri-apps/plugin-shell";
	import { platform } from "@tauri-apps/plugin-os";
	import { experiment_controller } from "$controllers/experiment.svelte";

	async function folderSearchHandler() {
		const path = await open({
			directory: true,
			multiple: false,
			defaultPath: (await getSavedWorkspacePath()) ?? (await homeDir()),
		});

		if (path) {
			await store.set("workspace_path", path);
			await workspace_controller.loadWorkspace(path);
		}
	}

	async function openerHandler() {
		if (platform() === "windows")
			await Command.create("code.cmd", [
				workspace_controller.path!,
			]).execute();
		else
			await Command.create("code", [
				workspace_controller.path!,
			]).execute();
	}
</script>

<div class="frow-2 bg-slate-200 rounded items-center p-2">
	<div class=" title">Workspace</div>
	<div class=" rounded bg-white grow px-2 h-full min-w-0">
		{#if workspace_controller.path}
			<div class="text-nowrap w-full overflow-x-scroll translate-y-1">
				{workspace_controller.path}
			</div>
		{:else}
			<div class="translate-y-1 italic text-slate-400">
				No workspace selected
			</div>
		{/if}
	</div>
	{#if workspace_controller.status === "loading"}
		<div class="icon-btn-sm bg-slate-500">
			<div class="  animate-spin text-slate-50">
				<LoaderCircle />
			</div>
		</div>
	{:else}
		{#if workspace_controller.status === "ready"}
			<button
				class="icon-btn-sm bg-slate-500 text-slate-50"
				onclick={openerHandler}><Keyboard /></button>
		{/if}
		{#if experiment_controller.editable}
			<button
				class="icon-btn-sm bg-slate-500 text-slate-50"
				onclick={folderSearchHandler}><FolderOpen /></button>
		{:else}
			<div class="icon-btn-sm bg-slate-300 text-slate-50">
				<FolderOpen />
			</div>
		{/if}
	{/if}
</div>
