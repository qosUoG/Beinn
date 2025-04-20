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

	async function folderSearchHandler() {
		const path = await open({
			directory: true,
			multiple: false,
			defaultPath: import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH,
		});

		if (path) workspace.connect(path);
	}

	async function saveHandler() {
		await workspace.save();
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
			<button class="icon-btn-sm slate" onclick={folderSearchHandler}
				><FolderOpen /></button>
			<button class="icon-btn-sm slate" onclick={saveHandler}
				><Disk /></button>
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
