<script lang="ts">
	import FolderOpen from "$icons/FolderOpen.svelte";
	import { open } from "@tauri-apps/plugin-dialog";
	import Mode from "./Mode.svelte";
	import Cli from "$icons/Cli.svelte";
	import { cli_panel } from "./CliPanelController.svelte";
	import Disk from "$icons/Disk.svelte";
	import Logs from "$icons/Logs.svelte";
	import { log_panel } from "./LogPanelController.svelte";
	import { workspace } from "$states/workspace.svelte";
	import Cancel from "$icons/Cancel.svelte";
	import { tick } from "svelte";
	import Loader from "$icons/Loader.svelte";
	import Tick from "$icons/Tick.svelte";
	import Cross from "$icons/Cross.svelte";

	let workspace_loading = $state(false);

	let show_save: "normal" | "success" | "fail" = $state("normal");

	async function folderSearchHandler() {
		const path = await open({
			directory: true,
			multiple: false,
			defaultPath: import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH,
		});

		if (path) {
			workspace_loading = true;
			await tick();
			await workspace.connect(path);
			workspace_loading = false;
		}
	}

	async function saveHandler() {
		await tick();
		const success = await workspace.save();
		show_save = success ? "success" : "fail";

		setTimeout(() => {
			show_save = "normal";
		}, 2000);
	}

	async function closeHandler() {
		workspace_loading = true;
		await tick();
		await workspace.kill();
		workspace_loading = false;
	}
</script>

<div class="h-[32px]" data-tauri-decorum-tb>
	<div class="frow-4 w-full px-24 py-1 justify-center" data-tauri-drag-region>
		<Mode />
		<div class="frow-1">
			<div class=" wrapped bg-slate-200 title">Workspace</div>
			<div class="wrapped rounded bg-slate-200 w-96 min-w-12 h-[24px]">
				<div class="text-nowrap w-full overflow-x-scroll">
					{workspace.path}
				</div>
			</div>
			{#if workspace_loading}
				<div class="icon-btn-sm bg-slate-200">
					<div class="animate-pulse">
						<Loader />
					</div>
				</div>
			{:else if !workspace.connected}
				<button class="icon-btn-sm slate" onclick={folderSearchHandler}
					><FolderOpen /></button>
			{:else}
				<button class="icon-btn-sm slate" onclick={closeHandler}
					><Cancel /></button>
			{/if}
			{#if !workspace.connected}
				<div class="icon-btn-sm bg-slate-200 text-white">
					<Disk />
				</div>
			{:else if show_save === "success"}
				<div class="icon-btn-sm green">
					<Tick />
				</div>
			{:else if show_save === "fail"}
				<div class="icon-btn-sm red">
					<Cross />
				</div>
			{:else}
				<button class="icon-btn-sm slate" onclick={saveHandler}
					><Disk /></button>
			{/if}
		</div>
		<button
			class="icon-btn-sm slate"
			onclick={() => {
				cli_panel.show = !cli_panel.show;
				log_panel.show = false;
			}}><Cli /></button>

		<button
			class="icon-btn-sm slate"
			onclick={() => {
				log_panel.show = !log_panel.show;
				cli_panel.show = false;
			}}><Logs /></button>
	</div>
</div>
