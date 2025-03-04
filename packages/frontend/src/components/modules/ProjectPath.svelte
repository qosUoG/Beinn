<script lang="ts">
	import Input from "$components/reuseables/Input.svelte";
	import { retryTillSuccess } from "$components/utils.svelte";
	import { getRandomId } from "$lib/utils";
	import {
		readDependency,
		setWorkspaceDirectory,
	} from "$services/backend.svelte";
	import { getAvailableEquipments } from "$services/qoslabapp.svelte";
	import { gstore } from "$states/global.svelte";
	import type { Equipment } from "qoslab-shared";
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

			let res: { module: string; cls: string }[] = [];

			await retryTillSuccess(5000, async () => {
				res = (await getAvailableEquipments()) as {
					module: string;
					cls: string;
				}[];
			});

			gstore.workspace.available_equipments = res;
		}}>Update</button>
</label>
