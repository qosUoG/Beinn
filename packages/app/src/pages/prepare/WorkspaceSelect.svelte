<script lang="ts">
	import { open } from "@tauri-apps/plugin-dialog";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import {
		Ban,
		Check,
		Cross,
		FolderOpen,
		Loader,
		Save,
	} from "@lucide/svelte";

	import { load, type Store } from "@tauri-apps/plugin-store";

	let store: Store;

	async function getSavedWorkspacePath() {
		if (!store) store = await load("workspace_path.json");
		return await store.get<string>("workspace_path");
	}

	import { homeDir } from "@tauri-apps/api/path";

	async function folderSearchHandler() {
		const path = await open({
			directory: true,
			multiple: false,
			defaultPath: (await getSavedWorkspacePath()) ?? (await homeDir()),
		});

		if (path) await workspace_controller.select(path);
	}

	async function saveHandler() {
		await workspace_controller.save();

		setTimeout(() => {
			workspace_controller.save_status = "normal";
		}, 2000);
	}

	function closeHandler() {
		workspace_controller.disconnect();
	}
</script>

<div class="frow-2 bg-slate-200 rounded items-center p-2">
	<div class=" title">Workspace</div>
	<div class=" rounded bg-white flex-grow px-2 h-full min-w-0">
		{#if workspace_controller.path}
			<div class="text-nowrap w-full overflow-x-scroll translate-y-[4px]">
				{workspace_controller.path}
			</div>
		{:else}
			<div class="translate-y-[4px] italic text-slate-400">
				No workspace selected
			</div>
		{/if}
	</div>
	<button class="icon-btn-sm slate" onclick={folderSearchHandler}
		><FolderOpen /></button>
</div>

<!-- <div class="frow-1">
	<div class=" wrapped bg-slate-200 title">Workspace</div>
	<div class="wrapped rounded bg-slate-200 w-96 min-w-12 h-[24px]">
		<div class="text-nowrap w-full overflow-x-scroll">
			{workspace_controller.path}
		</div>
	</div>
	{#if workspace_controller.connection === "connecting"}
		<div class="icon-btn-sm bg-slate-200">
			<div class="animate-pulse">
				<Loader />
			</div>
		</div>
	{:else if workspace_controller.connection === "disconnected"}
		<button class="icon-btn-sm slate" onclick={folderSearchHandler}
			><FolderOpen /></button>
	{:else if experiment_controller.closeable}
		<button class="icon-btn-sm slate" onclick={closeHandler}
			><Ban /></button>
	{:else}
		<div class="icon-btn-sm bg-slate-200 text-white">
			<Ban />
		</div>
	{/if}
	{#if workspace_controller.save_status === "saving"}
		<div class="icon-btn-sm bg-slate-200 text-white">
			<Save />
		</div>
	{:else if workspace_controller.save_status === "success"}
		<div class="icon-btn-sm green">
			<Check />
		</div>
	{:else if workspace_controller.save_status === "fail"}
		<div class="icon-btn-sm red">
			<Cross />
		</div>
	{:else}
		<button class="icon-btn-sm slate" onclick={saveHandler}
			><Save /></button>
	{/if}
</div> -->
