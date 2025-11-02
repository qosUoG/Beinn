<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import Label from "./Label.svelte";

	let {
		label,
		value = $bindable(),
		mandatory = false,
		editable = true,
	}: {
		label: string;
		value: string;
		mandatory?: boolean;
		editable?: boolean;
	} = $props();
</script>

<div class="frow items-center">
	<Label {label} {mandatory} />

	{#if experiment_controller.editable && editable}
		<div
			contenteditable="plaintext-only"
			bind:innerText={value}
			role={"input of " + label}
			class=" py-0.5 px-1 grow border-l border-slate-400 focus:outline-none text-wrap break-all wrap-anywhere"
			spellcheck="false"
			autocapitalize="off">
		</div>
	{:else}
		<div
			role={"input of " + label}
			class=" py-0.5 px-1 grow border-l border-slate-400 focus:outline-none text-wrap break-all wrap-anywhere min-h-5">
			{value}
		</div>
	{/if}
</div>
