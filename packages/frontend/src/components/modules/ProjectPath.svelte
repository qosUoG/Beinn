<script lang="ts">
	import Input from "$components/reuseables/Input.svelte";
	import { retryTillSuccess } from "$components/utils.svelte";
	import {
		readDependency,
		readModules,
		setWorkspaceDirectory,
	} from "$services/backend.svelte";
	import { getAvailableEquipments } from "$services/qoslabapp.svelte";
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
			// set the project directory
			gstore.workspace.directory = await setWorkspaceDirectory(
				gstore.workspace.path
			);

			// fetch the dependency from pyproject.toml
			gstore.workspace.dependencies = await readDependency();

			const modules = (await readModules()).modules.map((m) => m.name);

			await retryTillSuccess(5000, async () => {
				const eq = await getAvailableEquipments(modules);
			});
		}}>Update</button>
</label>
