<script lang="ts">
	import { gstore, type Log } from "$states/global.svelte";

	import Config from "$components/modules/config/Config.svelte";
	import Experiments from "$components/modules/runtime/Runtime.svelte";

	import CliPanel from "$components/modules/CliPanel.svelte";

	import Toast from "$components/modules/Toast.svelte";

	import Titlebar from "$components/modules/Titlebar.svelte";
	import { exit, relaunch } from "@tauri-apps/plugin-process";

	import { getCurrentWindow } from "@tauri-apps/api/window";
	getCurrentWindow().listen(
		"tauri://close-requested",
		async ({ event, payload }) => {
			await gstore.workspace.kill();

			await exit(0);
		}
	);
</script>

<div class="w-screen h-screen fcol max-h-screen max-w-screen">
	<Titlebar />

	<div class="w-full flex-grow rounded relative frow-4 px-2 pt-1 min-h-0">
		{#if gstore.mode === "Configuration"}
			<Config />
		{:else if gstore.mode === "Runtime"}
			<Experiments />
		{/if}

		<CliPanel />

		<Toast />
	</div>
</div>
