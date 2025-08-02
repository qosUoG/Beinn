<script lang="ts">
	import { open } from "@tauri-apps/plugin-dialog";

	import { tick } from "svelte";

	import { load, type Store } from "@tauri-apps/plugin-store";
	import { homeDir } from "@tauri-apps/api/path";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import {
		Ban,
		Check,
		Cross,
		FolderOpen,
		Loader,
		Save,
	} from "@lucide/svelte";

	let workspace_loading = $state(false);

	let show_save: "normal" | "success" | "fail" = $state("normal");

	async function folderSearchHandler() {
		const path = await open({
			directory: true,
			multiple: false,
			defaultPath: (await getSavedWorkspacePath()) ?? (await homeDir()),
		});

		if (path) {
			workspace_loading = true;
			await tick();
			await workspace_controller.connect(path);
			await tick();
			// if (workspace_controller.connected) await saveWorkspacePath(path);
			workspace_loading = false;
		}
	}

	async function saveHandler() {
		await tick();
		// const success = await workspace_controller.save();
		// show_save = success ? "success" : "fail";

		setTimeout(() => {
			show_save = "normal";
		}, 2000);
	}

	async function closeHandler() {
		workspace_loading = true;
		await tick();
		// await workspace_controller.kill();
		workspace_loading = false;
	}

	let store: Store;

	async function getSavedWorkspacePath() {
		if (!store) store = await load("workspace_path.json");
		return await store.get<string>("workspace_path");
	}

	async function saveWorkspacePath(path: string) {
		if (!store) store = await load("workspace_path.json");
		await store.set("workspace_path", path);
	}
</script>

<div class="h-[40px] frow w-full justify-center py-2">
	<div class="frow-4 z-1000">
		<div class="frow-1">
			<div class=" wrapped bg-slate-200 title">Workspace</div>
			<div class="wrapped rounded bg-slate-200 w-96 min-w-12 h-[24px]">
				<div class="text-nowrap w-full overflow-x-scroll">
					{workspace_controller.path}
				</div>
			</div>
			{#if workspace_loading}
				<div class="icon-btn-sm bg-slate-200">
					<div class="animate-pulse">
						<Loader />
					</div>
				</div>
			{:else if !workspace_controller.connected}
				<button class="icon-btn-sm slate" onclick={folderSearchHandler}
					><FolderOpen /></button>
			{:else}
				<button class="icon-btn-sm slate" onclick={closeHandler}
					><Ban /></button>
			{/if}
			{#if !workspace_controller.connected}
				<div class="icon-btn-sm bg-slate-200 text-white">
					<Save />
				</div>
			{:else if show_save === "success"}
				<div class="icon-btn-sm green">
					<Check />
				</div>
			{:else if show_save === "fail"}
				<div class="icon-btn-sm red">
					<Cross />
				</div>
			{:else}
				<button class="icon-btn-sm slate" onclick={saveHandler}
					><Save /></button>
			{/if}
		</div>
	</div>
</div>
