<script lang="ts">
	import { Tab } from "$controllers/analysis.svelte";

	import { cn } from "$components/utils.svelte";
	import { NotepadText, Trash2 } from "@lucide/svelte";
	import { debounce } from "$lib/utils";
	import Chart from "./Chart.svelte";

	let { tab = $bindable() }: { tab: Tab } = $props();

	const saveNoteDebounced = debounce((note) => {
		tab.save_note(note);
	}, 1000);

	const renameKeyDebounced = debounce((key) => {
		tab.rename_key(key);
	}, 1000);
</script>

<div class="frow-2 items-center p-1 justify-between">
	<div class="underline underline-offset-4">
		<input
			class=" text-xl font-thin"
			bind:this={tab.key_input}
			bind:value={
				() => tab.get_key(),
				(value) => {
					tab.set_key(value);
					renameKeyDebounced(value);
				}
			} />
	</div>

	<button
		class="p-1 rounded h-7 aspect-square bg-red-500 text-white"
		onclick={() => {}}>
		<Trash2 />
	</button>
</div>

<Chart bind:tab />

<div class=" bg-slate-800 rounded relative grow">
	<textarea
		bind:this={tab.note_textarea}
		bind:value={
			() => tab.get_note(),
			(value) => {
				tab.set_note(value);
				saveNoteDebounced(value);
			}
		}
		class=" resize-none w-full h-full outline-none focus:outline-none scrollbar-slate-400 text-white p-2 placeholder:text-white/80"
		spellcheck="false"
		autocomplete="off"
		autocapitalize="off"
		placeholder="Type your notes here..."></textarea>

	<span
		class=" text-slate-50/30 absolute w-20 h-20 p-6 top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 pointer-events-none">
		<NotepadText />
	</span>
</div>
