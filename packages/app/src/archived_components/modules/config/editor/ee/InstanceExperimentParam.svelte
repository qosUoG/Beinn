<script lang="ts">
	import { eeeditor } from "./EEEditorController.svelte";

	import SelectField from "$components/reuseables/Fields/SelectField.svelte";
	import { workspace } from "$states/workspace.svelte";

	let {
		key,
		instance_id = $bindable(),
	}: {
		key: string;
		instance_id: string;
	} = $props();

	let options = $derived(
		workspace.experiments.getInstanceables(eeeditor.id!)
	);
</script>

<SelectField {key} bind:value={instance_id} {options} />
