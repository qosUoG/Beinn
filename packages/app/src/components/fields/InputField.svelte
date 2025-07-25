<script lang="ts">
	import Label from "./Label.svelte";

	let {
		label,
		value = $bindable(),
		placeholder = "",
		mandatory = false,
	}: {
		label: string;
		value: string | number;
		placeholder?: string;
		mandatory?: boolean;
	} = $props();
</script>

<div class="frow items-center">
	<Label {label} {mandatory} />
	<input
		bind:value
		class=" py-0.5 px-1 placeholder:italic flex-grow w-fit border-l-1 border-slate-400"
		spellcheck="false"
		autocapitalize="off"
		autocomplete="off"
		{placeholder} />
</div>
