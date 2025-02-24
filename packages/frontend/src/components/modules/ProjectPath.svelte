<script lang="ts">
	import Input from "$components/reuseables/Input.svelte";
	import { gstore } from "$states/global.svelte";
	import { setWorkspaceDirectory } from "$services/backend.svelte";
</script>

<label class=" row-1 flex-grow">
	<div class="w-fit wrapped text-nowrap bg-slate-200 flex items-center">
		Project Directory
	</div>
	<Input
		spellcheck="false"
		class="flex-grow wrapped bg-slate-200"
		type="text"
		bind:value={gstore.project.path} />
	<button
		class="wrapped slate"
		onclick={async () => {
			gstore.project.directory = {
				files: await setWorkspaceDirectory(gstore.project.path),
				dirs: {},
			};
		}}>Update</button>
</label>
