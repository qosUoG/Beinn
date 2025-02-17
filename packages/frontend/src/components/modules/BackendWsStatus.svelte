<script>
	import { cn } from "$components/utils";

	import FilledCircle from "$icons/FilledCircle.svelte";
	import Refresh from "$icons/Refresh.svelte";
	import {
		backend_connection,
		backend_socket_connect,
	} from "$websockets/backend_ws.svelte";
</script>

<button
	class={cn(
		"wrapped bg-slate-200 row-2 items-center",
		backend_connection.connecting
			? "bg-green-100 text-green-800 cursor-default"
			: "bg-red-100 text-red-800"
	)}
	onclick={() => {
		if (!backend_connection.connecting) backend_socket_connect();
	}}>
	<div class="text-inherit">Backend</div>
	<div class="text-inherit icon-div flex items-center">
		{#if backend_connection.connecting}
			<FilledCircle />
		{:else}
			<Refresh />
		{/if}
	</div>
</button>
