<script lang="ts">
	import Plus from "$icons/Plus.svelte";

	import { getRandomId } from "$lib/utils";
	import { gstore } from "$states/global.svelte";
	import { editor } from "$components/modules/EditorController.svelte";
</script>

<div class="container col-2 bg-slate-200">
	<div class="row justify-between items-center">
		<div class="title">Equipment</div>
		<button
			class="icon-btn-sm bg-blue-200 text-blue-800"
			onclick={() => {
				const id = getRandomId(Object.keys(gstore.equipments));
				gstore.equipments[id] = { id };
			}}><Plus /></button>
	</div>
	{#each Object.values(gstore.equipments) as equipment}
		{#if gstore.equipments.path !== undefined}
			<button class="container">
				<div class="row-2">
					<div>Name</div>
					<div>{equipment.name}</div>
				</div>
			</button>
		{:else}
			<button
				class="container bg-white italic text-start text-slate-500/75"
				onclick={() => {
					editor.id = equipment.id;
					editor.mode = "Equipment";
				}}>Setup Equipment</button>
		{/if}
	{/each}
</div>
