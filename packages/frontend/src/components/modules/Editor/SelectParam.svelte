<script lang="ts">
	import { clickoutside, cn } from "$components/utils.svelte";
	import Separator from "./Separator.svelte";

	let open = $state(false);

	let {
		name,
		options = $bindable(),
		selection = $bindable(),
	}: {
		name: string;
		options: string[] | number[];
		selection: number;
	} = $props();

	let ParamElement: HTMLDivElement;
</script>

<div class=" row-2 bg-white wrapped items-center" bind:this={ParamElement}>
	<div class="editor-label">{name}</div>

	<Separator />
	<div class="relative flex-grow -m-2 px-2">
		<button
			class="w-full"
			onclick={(e) => {
				e.stopPropagation();
				open = true;
			}}>{options[selection]}</button>

		{#if open}
			<div
				use:clickoutside
				onoutsideclick={() => {
					open = false;
				}}
				class="absolute right-0 top-7 bg-white container col-1 w-full z-10 shadow-xl">
				{#each options as option, i}
					<button
						class={cn(
							" wrapped",
							selection === i
								? "bg-slate-400 text-slate-50"
								: "hover:bg-slate-200"
						)}
						onclick={() => {
							selection = i;
							open = false;
						}}>{option}</button>
				{/each}
			</div>
		{/if}
	</div>
</div>
