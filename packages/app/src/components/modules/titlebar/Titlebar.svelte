<script lang="ts">
	import { open } from "@tauri-apps/plugin-dialog";

	import { load, type Store } from "@tauri-apps/plugin-store";
	import { homeDir } from "@tauri-apps/api/path";
	import { workspace_controller } from "$controllers/workspace.svelte";

	import { experiment_controller } from "$controllers/experiment.svelte";
	import { cn } from "$components/utils.svelte";
	import { app_controller } from "$controllers/app.svelte";

	async function folderSearchHandler() {
		const path = await open({
			directory: true,
			multiple: false,
			defaultPath: (await getSavedWorkspacePath()) ?? (await homeDir()),
		});

		if (path) await workspace_controller.connect(path);
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

	let store: Store;

	async function getSavedWorkspacePath() {
		if (!store) store = await load("workspace_path.json");
		return await store.get<string>("workspace_path");
	}
</script>

<div class="h-[40px] frow w-full justify-center py-2">
	<div class="frow z-1000">
		<button
			class={cn(
				"px-2 text-center rounded-l",
				app_controller.page === "prepare"
					? "bg-slate-500 text-white"
					: "bg-slate-200"
			)}
			onclick={() => {
				app_controller.page = "prepare";
			}}>Preparation</button>
		<button
			class={cn(
				"px-2 text-center ",
				app_controller.page === "execute"
					? "bg-slate-500 text-white"
					: "bg-slate-200"
			)}
			onclick={() => {
				app_controller.page = "execute";
			}}>Experiment</button>
		<button
			class={cn(
				"px-2 text-center rounded-r",
				app_controller.page === "analyze"
					? "bg-slate-500 text-white"
					: "bg-slate-200"
			)}
			onclick={() => {
				app_controller.page = "analyze";
			}}>Analysis</button>
	</div>
</div>
