<script lang="ts">
	import { autofocus } from "$components/utils.svelte";
	import Separator from "./Separator.svelte";

	let { name = $bindable() } = $props();
</script>

<div class="row-2 w-full">
	<label class="row-2 bg-white wrapped w-full">
		<div class="editor-label">Name</div>
		<Separator />
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
	</label>
</div>
