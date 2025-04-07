<script lang="ts">
	import { gstore } from "$states/global.svelte";
	import { eeeditor } from "./EEEditorController.svelte";

	import SelectField from "$components/reuseables/Fields/SelectField.svelte";

	let {
		key,
		instance_id = $bindable(),
	}: {
		key: string;
		instance_id: string;
	} = $props();

	let options = $derived(
		gstore.workspace.experiments.getInstanceables(eeeditor.id!)
	);
</script>

<SelectField {key} bind:value={instance_id} {options} />
