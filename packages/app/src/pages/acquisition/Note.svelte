<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { debounce } from "$lib/utils";
	import { NotepadText } from "@lucide/svelte";

	const saveNoteDebounced = debounce((note) => {
		experiment_controller.experiment!.saveNote(note);
	}, 1000);
</script>

<div class=" bg-slate-800 rounded relative grow">
	{#if experiment_controller.experiment?.note !== undefined}
		<textarea
			bind:value={
				() => experiment_controller.experiment!.note!,
				(value) => {
					experiment_controller.experiment!.note = value;
					saveNoteDebounced(value);
				}
			}
			class=" resize-none w-full h-full outline-none focus:outline-none scrollbar-slate-400 text-white p-2 placeholder:text-white/80"
			spellcheck="false"
			autocomplete="off"
			autocapitalize="off"
			placeholder="Type your notes here..."></textarea>
	{/if}
	<span
		class=" text-slate-50/30 absolute w-full h-full p-6 top-0 left-0 pointer-events-none">
		<NotepadText />
	</span>
</div>
