<script lang="ts">
	import { autofocus, cn } from "$components/utils.svelte";
	import type { AllParamTypes } from "qoslab-shared";
	import InstanceParam from "./InstanceParam.svelte";
	import SelectParam from "./SelectParam.svelte";
	import Separator from "./Separator.svelte";

	let { params = $bindable() }: { params: Record<string, AllParamTypes> } =
		$props();

	$inspect(params);
</script>

{#each Object.entries(params) as [name, param]}
	{#if param.type === "int" || param.type === "float"}
		<label class="row-2 bg-white wrapped">
			<div class="editor-label">{name}</div>
			<Separator />
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
		</label>
	{:else if param.type === "bool"}
		<div class="row-2 bg-white wrapped w-full">
			<div class="editor-label">{name}</div>
			<Separator />
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
		</div>
	{:else if param.type === "str"}
		<label class="row-2 bg-white wrapped col-span-2">
			<div class="editor-label">{name}</div>
			<Separator />
			<input
				type="text"
				class="flex-grow"
				bind:value={param.value}
				onfocus={autofocus} />
		</label>
	{:else if param.type === "select.str" || param.type === "select.int" || param.type === "select.float"}
		<SelectParam {name} bind:value={param.value} options={param.options} />
	{:else if param.type === "instance"}
		<InstanceParam {name} bind:instance_name={param.instance_name} />
	{:else}
		{param.type} is not handled !!!
	{/if}
{/each}
