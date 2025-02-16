<script lang="ts">
	import { backend_socket, sendSetDirectory } from "$websockets/backend_ws";
	import Input from "$components/reuseables/Input.svelte";

	backend_socket;

	let path = $state("/Users/harry/Downloads");
</script>

<label class="p-4 flex gap-2 items-center">
	<div class="w-fit bg-slate-200 rounded p-1 px-2 text-nowrap">
		Project Path
	</div>
	<Input
		spellcheck="false"
		class="flex-grow bg-slate-200 rounded p-1 px-2"
		type="text"
		bind:value={path} />
	<button
		class="bg-green-100 rounded p-1 px-2 text-green-900"
		onclick={() => {
			sendSetDirectory($state.snapshot(path));
		}}>Update</button>
</label>
