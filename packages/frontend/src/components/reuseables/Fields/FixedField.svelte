<script lang="ts">
	import Separator from "../Separator.svelte";

	let { key, value }: { key: string; value: string } = $props();
</script>

<div class=" row-2 bg-white wrapped min-w-0 flex-grow">
	<div class="editor-label">{key}</div>
	<Separator />
	<div>{value}</div>
</div>
