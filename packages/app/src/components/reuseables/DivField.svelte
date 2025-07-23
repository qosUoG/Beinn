<script lang="ts">
	import type { Snippet } from "svelte";
	import Separator from "./Separator.svelte";

	let { key, children }: { key: string; children: Snippet } = $props();
</script>

<div class=" frow-2 bg-white rounded min-w-0 flex-grow wrapped">
	<div class="editor-label">{key}</div>
	<Separator />

	{@render children?.()}
</div>
