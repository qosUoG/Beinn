<script lang="ts">
	import LabelField from "$components/reuseables/Fields/LabelField.svelte";
	import { autofocus } from "$components/utils.svelte";
	import Separator from "../../../reuseables/Separator.svelte";

	let { name = $bindable() } = $props();
</script>

<LabelField key="Name">
	<input
		type="text"
		class="w-full"
		onkeydown={(e: KeyboardEvent) => {
			if (e.key === "Backspace" || e.key === "Delete") return;
			if (/[A-Za-z0-9_\- ]/.test(e.key)) return;

			e.preventDefault();
		}}
		bind:value={name}
		onfocus={autofocus} />
</LabelField>
