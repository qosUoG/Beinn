<script lang="ts">
	import { clickoutside, cn } from "$components/utils.svelte";
	import { getRandomId } from "$lib/utils";
	import { gstore } from "$states/global.svelte";
	import { eeeditor } from "./EEEditorController.svelte";
	import Separator from "./Separator.svelte";

	let open = $state(false);

	let {
		name,
		instance_name = $bindable(),
	}: {
		name: string;
		instance_name: string;
	} = $props();

	let ParamElement: HTMLDivElement;

	let options = $derived(
		Object.entries(gstore.equipments)
			.filter(
				([id, e]) => id !== eeeditor.id && e.name && e.name.length > 0
			)
			.map(([_, e]) => e.name!)
	);

	const id = getRandomId([]);
</script>

<div class=" row-2 bg-white wrapped items-center" bind:this={ParamElement}>
	<div class="eeeditor-label">{name}</div>

	<Separator />
	<div class="relative flex-grow -m-2 px-2">
		<button
			{id}
			class="w-full min-w-full block"
			onclick={(e) => {
				e.stopPropagation();
				open = true;
			}}>
			{#if instance_name}
				<div>
					{instance_name}
				</div>
			{:else}
				<div class="text-slate-400 italic">select instance</div>
			{/if}
		</button>

		{#if open}
			<div
				use:clickoutside={id}
				onoutsideclick={() => {
					open = false;
				}}
				class="absolute right-0 top-7 bg-white container col-1 w-full z-10 shadow-xl">
				{#each options as option}
					<button
						class={cn(
							" wrapped",
							instance_name === option
								? "bg-slate-400 text-slate-50"
								: "hover:bg-slate-200"
						)}
						onclick={() => {
							instance_name = option;
							open = false;
						}}>{option}</button>
				{/each}
			</div>
		{/if}
	</div>
</div>
