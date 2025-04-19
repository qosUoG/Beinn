<script lang="ts">
	import FolderOpen from "$icons/FolderOpen.svelte";
	import { gstore } from "$states/global.svelte";
	import { open } from "@tauri-apps/plugin-dialog";
	import Mode from "./Mode.svelte";
	import Cli from "$icons/Cli.svelte";
	import { cli_panel } from "./CliPanelController.svelte";
	import Disk from "$icons/Disk.svelte";
	import { toastError } from "./ToastController.svelte";
	import type { Err } from "$states/err";

	async function folderSearchHandler() {
		const path = await open({
			directory: true,
			multiple: false,
			defaultPath: import.meta.env.VITE_DEFAULT_EXPERIMENT_PATH,
		});

		if (path) gstore.workspace.connect(path);
	}

	async function saveHandler() {
		try {
			await gstore.workspace.save();
		} catch (e) {
			toastError(e as Err);
		}
	}
</script>

<div class="h-[32px]" data-tauri-decorum-tb>
	<div class="frow-4 w-full px-24 py-1 justify-center" data-tauri-drag-region>
		<Mode />
		<div class="frow-1">
			<div class=" wrapped bg-slate-200 title">Workspace</div>
			<div class="wrapped rounded bg-slate-200 w-96 min-w-12 h-[24px]">
				<div class="text-nowrap w-full overflow-x-scroll">
					{gstore.workspace.path}
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
			}}><Cli /></button>
	</div>
</div>
