<script lang="ts">
	import Cross from "$icons/Cross.svelte";
	import { content } from "./ToastController.svelte";
</script>

{#each Object.entries(content) as [id, text]}
	<div
		class="absolute wrapped bg-white z-1000 left-1/2 -translate-x-1/2 bottom-8 w-128 frow items-center">
		<div class="flex-grow text-center wrapped">
			{text}
		</div>
		<button
			class="icon-btn-sm"
			onclick={() => {
				delete content[id];
			}}><Cross /></button>
	</div>
{/each}
