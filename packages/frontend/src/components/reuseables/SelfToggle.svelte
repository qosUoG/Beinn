<script lang="ts">
	import CheckedSquare from "$icons/CheckedSquare.svelte";
	import Square from "$icons/Square.svelte";

	let { key, value = $bindable() }: { key: string; value: boolean } =
		$props();
</script>

<button
	class=" row-2 bg-white min-w-0 rounded relative pl-6"
	onclick={() => {
		value = !value;
	}}>
	<div class="absolute left-0 icon-btn-sm">
		{#if value}
			<CheckedSquare />
		{:else}
			<Square />
		{/if}
	</div>
	<div class="editor-label wrapped">{key}</div>
</button>
