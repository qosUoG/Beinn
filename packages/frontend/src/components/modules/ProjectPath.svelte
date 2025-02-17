<script lang="ts">
	import Input from "$components/reuseables/Input.svelte";
	import { gstore } from "$states/global.svelte";
	import { sendSetDirectory } from "$websockets/backend_ws.svelte";

	console.log(JSON.stringify(gstore, null, 4));
</script>

<label class=" row-1 flex-grow">
	<div class="w-fit wrapped text-nowrap bg-slate-200 flex items-center">
		Project Directory
	</div>
	<Input
		spellcheck="false"
		class="flex-grow wrapped bg-slate-200"
		type="text"
		bind:value={gstore.workspace.path}
	/>
	<button
		class="wrapped text-green-800 bg-green-100"
		onclick={() => {
			sendSetDirectory(gstore.workspace.path);
		}}>Update</button
	>
</label>
