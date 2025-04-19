<script lang="ts">
	import { gstore, type Log } from "$states/global.svelte";

	import Config from "$components/modules/config/Config.svelte";
	import Experiments from "$components/modules/runtime/Runtime.svelte";

	import CliPanel from "$components/modules/CliPanel.svelte";

	import Toast from "$components/modules/Toast.svelte";

	import Titlebar from "$components/modules/Titlebar.svelte";

	// function connectWs() {
	// 	// Connect to backend
	// 	let ws = new WebSocket(backendWs("cli"));
	// 	ws.onmessage = async (event: MessageEvent<string>) => {
	// 		const payload = JSON.parse(event.data) as { logs: Log[] };
	// 		await gstore.logs.push(payload.logs);
	// 	};
	// 	ws.onclose = () => {
	// 		// Recursively reconnect
	// 		connectWs();
	// 	};
	// }

	// window.addEventListener("beforeunload", (e) => {
	// 	e.preventDefault();
	// });
</script>

<div class="w-screen h-screen fcol">
	<Titlebar />

	<div class="w-full flex-grow rounded p-2 relative frow-4">
		{#if gstore.mode === "Configuration"}
			<Config />
		{:else if gstore.mode === "Runtime"}
			<Experiments />
		{/if}

		<CliPanel />

		<Toast />
	</div>
</div>
