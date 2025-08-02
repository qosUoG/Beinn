<script lang="ts">
	import DropSelect from "$components/fields/DropSelect.svelte";
	import InputField from "$components/fields/InputField.svelte";
	import TabSelect from "$components/fields/TabSelect.svelte";
	import { equipment_controller } from "$controllers/equipment.svelte";
	import type { SimpleParamType } from "$controllers/params.svelte";

	let {
		label,
		param = $bindable(),
	}: { label: string; param: SimpleParamType } = $props();
</script>

{#if param.type === "int" || param.type === "float" || param.type === "str"}
	<InputField
		{label}
		bind:value={param.value}
		onkeydown={(e: KeyboardEvent) => {
			if (param.type === "str") return;

			if (
				e.key === "Backspace" ||
				e.key === "Delete" ||
				e.key === "ArrowLeft" ||
				e.key === "ArrowRight"
			)
				return;
			if (/[0-9]/.test(e.key)) return;
			if (e.key === "." && param.type === "float") return;

			e.preventDefault();
		}} />
{:else if param.type === "bool"}
	<TabSelect
		{label}
		bind:value={param.value}
		items={[
			{ key: "True", value: true },
			{ key: "False", value: false },
		]} />
{:else if param.type === "select.float" || param.type === "select.int" || param.type === "select.str"}
	<DropSelect {label} bind:value={param.value} options={param.options} />
{:else if param.type === "instance.equipment"}
	<DropSelect
		{label}
		bind:value={param.name}
		options={Object.keys(equipment_controller.instances)} />
{:else if param.type === "instance.experiment"}
	<!-- TODO -->
	<!-- <DropSelect
		{label}
		bind:value={param.name}
		options={Object.keys(experiment_controller.experiments)} /> -->
{/if}
