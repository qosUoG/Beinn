<script lang="ts">
	import Titlebar from "$components/modules/titlebar/Titlebar.svelte";
	import { exit } from "@tauri-apps/plugin-process";

	import { getCurrentWindow } from "@tauri-apps/api/window";

	import Config from "$components/modules/config/Config.svelte";
	import { workspace_controller } from "$controllers/WorkspaceController.svelte";

	getCurrentWindow().listen("tauri://close-requested", async () => {
		// const should_kill = await workspace.kill();
		// if (should_kill) await exit(0);
	});
</script>

<div class="w-screen h-screen fcol max-h-screen max-w-screen">
	<Titlebar />

	<div class="w-full flex-grow rounded relative frow-4 p-2 pt-0 min-h-0">
		<Config />
		<!-- {#if mode_controller.mode === "Configuration"}
			<Config />
		{:else if mode_controller.mode === "Runtime"}
			<Experiments />
		{/if} -->

		<!-- <CliPanel />

		<LogPanel /> -->
	</div>
</div>
