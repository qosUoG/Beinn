<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
</script>

{#if experiment_controller.experiment}
	<div class=" rounded bg-slate-200 flex-grow p-2 frow-2 items-start">
		<div class="title">Notes</div>
		<textarea
			bind:value={
				() => experiment_controller.experiment!.note,
				(value) => {
					experiment_controller.experiment!.saveNote(value);
				}
			}
			class=" resize-none w-full h-full outline-none focus:outline-none scrollbar-slate-400"
			spellcheck="false"
			autocomplete="off"
			autocapitalize="off"></textarea>
	</div>
{/if}
