<script lang="ts">
	import Select from "$components/reuseables/Select.svelte";
	import Separator from "./Separator.svelte";

	let {
		name,
		options = $bindable(),
		value = $bindable(),
	}: {
		name: string;
		options: string[] | number[];
		value: number | string;
	} = $props();
</script>

<div class=" row-2 bg-white wrapped min-w-0 h-full">
	<div class="editor-label">{name}</div>

	<Separator />
	<div class="relative flex-grow -mx-2 px-2 flex items-center min-w-0 h-full">
		<Select bind:value {options} />
	</div>
</div>
