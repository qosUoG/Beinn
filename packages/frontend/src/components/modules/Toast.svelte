<script lang="ts">
	import Cross from "$icons/Cross.svelte";
	import { content } from "./ToastController.svelte";
</script>

{#each Object.entries(content) as [id, text]}
	<div
		class="absolute wrapped bg-white z-1000 left-1/2 -translate-x-1/2 bottom-8 w-128 frow items-start">
		<div class="flex-grow text-left wrapped break-all mr-4">
			{text}
		</div>
		<button
			class="icon-btn-sm absolute top-2 right-2 h-fit"
			onclick={() => {
				delete content[id];
			}}><Cross /></button>
	</div>
{/each}
