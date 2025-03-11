<script lang="ts">
	import Select from "$components/reuseables/Select.svelte";
	import { gstore } from "$states/global.svelte";
	import { eeeditor } from "./EEEditorController.svelte";
	import Separator from "./Separator.svelte";

	let open = $state(false);

	let {
		name,
		instance_name = $bindable(),
	}: {
		name: string;
		instance_name: string;
	} = $props();

	let options = $derived(
		Object.entries(gstore.equipments)
			.filter(
				([id, e]) => id !== eeeditor.id && e.name && e.name.length > 0
			)
			.map(([_, e]) => e.name!)
	);
</script>

<div class=" row-2 bg-white wrapped">
	<div class="eeeditor-label">{name}</div>

	<Separator />
	<div class="relative flex-grow -mx-2 px-2 flex items-center min-w-0">
		<Select bind:value={instance_name} {options} />
	</div>
</div>
