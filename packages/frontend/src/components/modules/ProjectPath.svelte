<script lang="ts">
	import Input from "$components/reuseables/Input.svelte";
	import { gstore } from "$states/global.svelte";
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
		bind:value={gstore.project.path} />
	<button
		class="wrapped text-green-800 bg-green-100"
		onclick={async () => {
			const res = await (
				await fetch(
					`http://localhost:8000/getDirectoryContent/${encodeURIComponent(gstore.project.path)}`
				)
			).json();

			gstore.project.directory = { files: res, dirs: {} };
		}}>Update</button>
</label>
