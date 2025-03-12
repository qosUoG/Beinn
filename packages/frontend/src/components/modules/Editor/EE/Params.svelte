<script lang="ts">
	import { autofocus, cn } from "$components/utils.svelte";
	import type { AllParamTypes } from "qoslab-shared";
	import InstanceParam from "./InstanceParam.svelte";
	import SelectParam from "./SelectParam.svelte";
	import LabelField from "$components/reuseables/Fields/LabelField.svelte";
	import DivField from "$components/reuseables/Fields/DivField.svelte";

	let { params = $bindable() }: { params: Record<string, AllParamTypes> } =
		$props();
</script>

{#each Object.entries(params) as [key, param]}
	{#if param.type === "int" || param.type === "float"}
		<LabelField {key}>
			<input
				type="number"
				class=""
				bind:value={param.value}
				onkeydown={(e: KeyboardEvent) => {
					if (e.key === "Backspace" || e.key === "Delete") return;
					if (/[0-9]/.test(e.key)) return;

					e.preventDefault();
				}}
				onfocus={autofocus} />
			{#if param.suffix}
				{param.suffix}
			{/if}
		</LabelField>
	{:else if param.type === "bool"}
		<DivField {key}>
			<div class="grid grid-cols-2 flex-grow">
				<button
					class={cn(
						"  rounded ",
						param.value === true ? "bg-slate-400 text-slate-50" : ""
					)}
					onclick={() => {
						param.value = true;
					}}>True</button>
				<button
					class={cn(
						" rounded",
						param.value === false
							? "bg-slate-400 text-slate-50"
							: ""
					)}
					onclick={() => {
						param.value = false;
					}}>False</button>
			</div>
		</DivField>
	{:else if param.type === "str"}
		<LabelField {key}>
			<input
				type="text"
				class="flex-grow"
				bind:value={param.value}
				onfocus={autofocus} />
		</LabelField>
	{:else if param.type === "select.str" || param.type === "select.int" || param.type === "select.float"}
		<SelectParam {key} bind:value={param.value} options={param.options} />
	{:else if param.type === "instance"}
		<InstanceParam {key} bind:instance_name={param.instance_name} />
	{:else}
		{param.type} is not handled !!!
	{/if}
{/each}
