<script lang="ts">
	import { zeropad } from "$lib/utils";

	let { time, class: clazz = "" }: { time: number; class?: string } =
		$props();

	const t = new Date(time);
	const hour = t.getHours() - 1;
	const minuet = t.getMinutes();
	const second = t.getSeconds();
</script>

<div class={clazz}>
	{#if hour > 0}
		{zeropad(hour)}h {zeropad(minuet)}m
	{:else if minuet > 0}
		{zeropad(minuet)}m {zeropad(second)}s
	{:else}
		{zeropad(second)}s
	{/if}
</div>
