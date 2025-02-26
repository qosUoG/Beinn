<script lang="ts">
	import Select from "$components/reuseables/Select.svelte";
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
		<Select bind:open bind:selection {options} />
	</div>
</div>
