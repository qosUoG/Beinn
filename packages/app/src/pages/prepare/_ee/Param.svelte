<script lang="ts">
	import ContentEditable from "$components/fields/ContentEditable.svelte";
	import DropSelect from "$components/fields/DropSelect.svelte";
	import InputField from "$components/fields/InputField.svelte";
	import TabSelect from "$components/fields/TabSelect.svelte";
	import { equipment_controller } from "$controllers/equipment.svelte";
	import type { RuntimeSimpleParamType } from "$controllers/params.svelte";
	import { tick } from "svelte";

	let {
		label,
		param = $bindable(),
		saveFn,
		editable = true,
	}: {
		label: string;
		param: RuntimeSimpleParamType;
		saveFn: () => Promise<void>;
		editable?: boolean;
	} = $props();
</script>

{#if param.type === "int" || param.type === "float"}
	<InputField
		{editable}
		mandatory={param.required}
		{label}
		bind:value={
			() => param.value,
			(v: string | number) => {
				if (param.type === "int") param.value = parseInt(v as string);
				else param.value = parseFloat(v as string);

				saveFn();
			}
		}
		onkeydown={(e: KeyboardEvent) => {
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
{:else if param.type === "str"}
	<ContentEditable
		{editable}
		mandatory={param.required}
		{label}
		bind:value={
			() => param.value,
			(v: string) => {
				param.value = v;
				saveFn();
			}
		} />
{:else if param.type === "bool"}
	<TabSelect
		{editable}
		mandatory={param.required}
		{label}
		bind:value={
			() => param.value,
			(v: boolean) => {
				param.value = v;
				saveFn();
			}
		}
		items={[
			{ key: "True", value: true },
			{ key: "False", value: false },
		]} />
{:else if param.type === "select.float" || param.type === "select.int" || param.type === "select.str"}
	<DropSelect
		{editable}
		mandatory={param.required}
		{label}
		bind:value={
			() => ({ key: `${param.value}`, value: param.value }),
			(v) => {
				param.value = v.value;
				saveFn();
			}
		}
		options={param.options.map((o) => ({ key: `${o}`, value: o }))} />
{:else if param.type === "instance.equipment"}
	<DropSelect
		{editable}
		mandatory={param.required}
		{label}
		bind:value={
			() => ({
				key: param.value ?? "",
				value: param.instance,
			}),
			(v) => {
				param.value = v.key;
				param.instance = v.value;
				saveFn();
			}
		}
		options={[
			...equipment_controller.equipment_names.map((n) => {
				const equipment = equipment_controller.equipments.find(
					(e) => e.name === n
				);
				return {
					key: equipment?.name ?? "",
					value: equipment,
				};
			}),
			{ key: "", value: undefined },
		]} />
	<!-- {:else if param.type === "instance.experiment"} -->

	<!-- <DropSelect
		{label}
		bind:value={param.name}
		options={Object.keys(experiment_controller.experiments)} /> -->
{/if}
