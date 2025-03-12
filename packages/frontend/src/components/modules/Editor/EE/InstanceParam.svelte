<script lang="ts">
	import Select from "$components/reuseables/Select.svelte";
	import { gstore } from "$states/global.svelte";
	import { eeeditor } from "./EEEditorController.svelte";
	import Separator from "../../../reuseables/Separator.svelte";
	import SelectField from "$components/reuseables/Fields/SelectField.svelte";

	let open = $state(false);

	let {
		key,
		instance_name = $bindable(),
	}: {
		key: string;
		instance_name: string;
	} = $props();

	let options = $derived(
		Object.values(gstore.equipments)
			.filter((e) => e.created) // Split here for type check sake
			.filter((e) => e.id !== eeeditor.id && e.name && e.name.length > 0)
			.map((e) => e.name!)
	);
</script>

<SelectField {key} bind:value={instance_name} {options} />
