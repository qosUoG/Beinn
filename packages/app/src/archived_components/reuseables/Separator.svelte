<script lang="ts">
	import { cn } from "$components/utils.svelte";

	let { class: clazz = "bg-slate-200" }: { class?: string } = $props();
</script>

<div class={cn("  rounded-full p-[1px]", clazz)}></div>
