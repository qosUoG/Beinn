<script lang="ts">
	import { zeropad } from "$lib/utils";

	let { time, class: clazz = "" }: { time: number; class?: string } =
		$props();

	const hour = Math.floor(time / 3600000);
	const minuet = Math.floor((time % 3600000) / 60000);
	const second = Math.floor((time % 60000) / 1000);
</script>

<div class={clazz}>
	{#if time < 0}
		-
	{:else if hour > 0}
		{zeropad(hour)}h {zeropad(minuet)}m
	{:else if minuet > 0}
		<!-- {console.log({ time, hour, minuet, second })} -->
		{zeropad(minuet)}m {zeropad(second)}s
	{:else}
		{zeropad(second)}s
	{/if}
</div>
