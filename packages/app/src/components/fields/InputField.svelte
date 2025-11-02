<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import Label from "./Label.svelte";

	let {
		label,
		value = $bindable(),
		placeholder = "",
		mandatory = false,
		onkeydown = () => {},
		onfocus = () => {},
		editable = true,
	}: {
		label: string;
		value: string | number;
		placeholder?: string;
		mandatory?: boolean;
		onkeydown?: (e: KeyboardEvent) => void;
		onfocus?: (e: FocusEvent) => void;
		editable?: boolean;
	} = $props();
</script>

<div class="frow items-center">
	<Label {label} {mandatory} />
	{#if experiment_controller.editable && editable}
		<input
			bind:value
			class=" py-0.5 px-1 placeholder:italic placeholder:text-center grow w-fit border-l border-slate-400"
			spellcheck="false"
			autocapitalize="off"
			autocomplete="off"
			{onkeydown}
			{onfocus}
			{placeholder} />
	{:else}
		<div class="py-0.5 px-1 grow w-fit border-l border-slate-400 min-h-5">
			{value}
		</div>
	{/if}
</div>
