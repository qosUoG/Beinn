<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import { Tab } from "$controllers/analysis.svelte";
	import { onMount } from "svelte";

	let { tab = $bindable() }: { tab: Tab } = $props();

	tab.plot();

	$effect(() => {
		tab.plot();
	});

	const modes = ["lines", "markers", "lines+markers"] as const;
</script>

<div class="bg-slate-700 rounded p-2 grid grid-cols-2 gap-2">
	<div class="frow-4 items-center">
		<div class="text-white">x axis</div>
		<div class="frow-1 flex-wrap">
			{#each tab.titles as title}
				<button
					class={cn(
						"  rounded px-2 py-0.5 border text-white",
						tab.content!.x === title
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
		<div class="text-white">y axis</div>
		<div class="frow-1 flex-wrap">
			{#each tab.titles as title}
				<button
					class={cn(
						"  rounded px-2 py-0.5 border text-white",
						tab.content!.y.includes(title)
							? "border-white"
							: " border-slate-700"
					)}
					onclick={() => {
						tab.toggle_y(title);
					}}>
					{title}
				</button>
			{/each}
		</div>
	</div>
	<div class="frow-4 items-center">
		<div class="text-white">y label</div>
		<input
			class="border border-white w-32 rounded py-0.5 px-1 text-white"
			bind:value={
				() => tab.content!.y_label,
				(value) => {
					tab.set_y_label(value);
				}
			} />
	</div>
	<div class="frow-4 items-center">
		<div class="text-white">mode</div>
		<div class="frow-1">
			{#each modes as mode}
				<button
					class={cn(
						"  rounded px-2 py-0.5 border text-white",
						tab.content!.mode === mode
							? "border-white"
							: " border-slate-700"
					)}
					onclick={() => {
						tab.set_mode(mode);
					}}>
					{mode}
				</button>
			{/each}
		</div>
	</div>
	<div class="frow-4 items-center">
		<div class="text-white">x label</div>
		<input
			class="border border-white w-32 rounded py-0.5 px-1 text-white"
			bind:value={
				() => tab.content!.x_label,
				(value) => {
					tab.set_x_label(value);
				}
			} />
	</div>
</div>

<div class="p-1 rounded bg-white">
	<div id="plotly:div"></div>
</div>
