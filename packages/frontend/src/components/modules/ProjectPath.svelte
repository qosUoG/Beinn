<script lang="ts">
	import Input from "$components/reuseables/Input.svelte";
	import { setWorkspaceDirectory } from "$services/backend.svelte";
	import { gstore } from "$states/global.svelte";
</script>

<label class=" row-1 flex-grow">
	<div class="w-fit wrapped text-nowrap bg-slate-200 flex items-center">
		Project Directory
	</div>
	<Input
		spellcheck="false"
		class="flex-grow wrapped bg-slate-200"
		type="text"
		bind:value={gstore.workspace.path} />
	<button
		class="wrapped slate"
		onclick={async () => {
			gstore.workspace.directory = await setWorkspaceDirectory(
				gstore.workspace.path
			);
		}}>Update</button>
</label>
