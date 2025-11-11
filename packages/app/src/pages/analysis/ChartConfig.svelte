<script lang="ts">
	import { Tab } from "$controllers/analysis.svelte";

	import { cn } from "$components/utils.svelte";

	let { tab = $bindable() }: { tab: Tab } = $props();
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
