<script lang="ts">
	import Label from "./Label.svelte";

	let {
		label,
		value = $bindable(),
		placeholder = "",
		mandatory = false,
		onkeydown = () => {},
		onfocus = () => {},
	}: {
		label: string;
		value: string | number;
		placeholder?: string;
		mandatory?: boolean;
		onkeydown?: (e: KeyboardEvent) => void;
		onfocus?: (e: FocusEvent) => void;
	} = $props();
</script>

<div class="frow items-center">
	<Label {label} {mandatory} />
	<input
		bind:value
		class=" py-0.5 px-1 placeholder:italic placeholder:text-center flex-grow w-fit border-l-1 border-slate-400"
		spellcheck="false"
		autocapitalize="off"
		autocomplete="off"
		{onkeydown}
		{placeholder} />
</div>
