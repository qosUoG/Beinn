<script lang="ts">
	import { mode_controller } from "$components/modules/ModeController.svelte";

	import Config from "$components/modules/config/Config.svelte";
	import Experiments from "$components/modules/runtime/Runtime.svelte";

	import CliPanel from "$components/modules/CliPanel.svelte";

	import Titlebar from "$components/modules/Titlebar.svelte";
	import { exit } from "@tauri-apps/plugin-process";

	import { getCurrentWindow } from "@tauri-apps/api/window";
	import LogPanel from "$components/modules/LogPanel.svelte";
	import { workspace } from "$states/workspace.svelte";

	getCurrentWindow().listen("tauri://close-requested", async () => {
		await workspace.kill();

		await exit(0);
	});
</script>

<div class="w-screen h-screen fcol max-h-screen max-w-screen">
	<Titlebar />

	<div class="w-full flex-grow rounded relative frow-4 p-2 pt-1 min-h-0">
		{#if mode_controller.mode === "Configuration"}
			<Config />
		{:else if mode_controller.mode === "Runtime"}
			<Experiments />
		{/if}

		<CliPanel />

		<LogPanel />
	</div>
</div>
