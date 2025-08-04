<script lang="ts">
	import Label from "./Label.svelte";

	let {
		label,
		value = $bindable(),
		mandatory = false,
	}: {
		label: string;
		value: string;
		mandatory?: boolean;
	} = $props();
</script>

<div class="frow items-center">
	<Label {label} {mandatory} />

	<div
		contenteditable="plaintext-only"
		bind:innerText={value}
		role={"input of " + label}
		class=" py-0.5 px-1 flex-grow border-l-1 border-slate-400 focus:outline-none text-wrap break-all wrap-anywhere"
		spellcheck="false"
		autocapitalize="off">
	</div>
</div>
