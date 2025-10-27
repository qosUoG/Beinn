<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
</script>

<textarea
	bind:value={
		() => experiment_controller.experiment!.note!,
		(value) => {
			experiment_controller.experiment!.saveNote(value);
		}
	}
	class=" resize-none w-full h-full outline-none focus:outline-none scrollbar-slate-400 text-white p-2 placeholder:text-white/80"
	spellcheck="false"
	autocomplete="off"
	autocapitalize="off"
	placeholder="Type your notes here..."></textarea>
