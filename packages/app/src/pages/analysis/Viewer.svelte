<script lang="ts">
	import { Tab } from "$controllers/analysis.svelte";

	import { cn } from "$components/utils.svelte";
	import { NotepadText } from "@lucide/svelte";
	import { debounce } from "$lib/utils";
	import Chart from "./Chart.svelte";

	let { tab = $bindable() }: { tab: Tab } = $props();

	const saveNoteDebounced = debounce((note) => {
		tab.save_note(note);
	}, 1000);
</script>

<div class="bg-slate-700 rounded p-2 fcol-1">
	<div class="frow-4 items-center">
		<div class="text-white">x axis:</div>
		<div class="frow-1">
			{#each tab.titles as title}
				<button
					class={cn(
						"  rounded px-2 py-0.5 border text-white",
						tab.get_x() === title
							? "border-white"
							: " border-slate-700"
					)}
					onclick={() => {
						tab.set_x(title);
					}}>
					{title}
				</button>
			{/each}
		</div>
	</div>
	<div class="frow-4 items-center">
		<div class="text-white">y axis:</div>
		<div class="frow-1 flex-wrap">
			{#each tab.titles as title}
				<button
					class={cn(
						"  rounded px-2 py-0.5 border text-white",
						tab.y_includes(title)
							? "border-white"
							: " border-slate-700"
					)}
					onclick={async () => {
						await tab.toggle_y(title);
					}}>
					{title}
				</button>
			{/each}
		</div>
	</div>
	<div class="frow-4 items-center">
		<div class="text-white">y label:</div>
		<input
			class="border border-white w-32 rounded py-0.5 px-1 text-white"
			bind:value={
				() => tab.get_y_label(),
				(value) => {
					tab.set_y_label(value);
				}
			} />
	</div>
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
