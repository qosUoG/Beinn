<script lang="ts">
	import { gstore } from "$states/global.svelte";
	import { eeeditor } from "./EEEditorController.svelte";

	import SelectField from "$components/reuseables/Fields/SelectField.svelte";

	let open = $state(false);

	let {
		key,
		instance_id = $bindable(),
	}: {
		key: string;
		instance_id: string;
	} = $props();

	let options = $derived(
		Object.values(gstore.equipments)
			// Split here for type check sake
			.filter((e) => e.created)
			// Name needs to be defiend
			.filter((e) => e.id !== eeeditor.id && e.name && e.name.length > 0)
			.map((e) => ({ key: e.name, value: e.id }))
	);
</script>

<SelectField {key} bind:value={instance_id} {options} />
