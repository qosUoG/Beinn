<script lang="ts" generics="T extends string | number">
	import SelectField from "$components/reuseables/Fields/SelectField.svelte";

	let {
		key,
		options = $bindable(),
		value = $bindable(),
	}: { key: string; value: T; options: T[] } = $props();
</script>

<SelectField {key} bind:value {options} />
