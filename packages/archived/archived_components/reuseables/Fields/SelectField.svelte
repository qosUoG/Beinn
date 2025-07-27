<script lang="ts" generics="T extends string | number">
	import Select from "../Select.svelte";

	import Separator from "../Separator.svelte";

	let {
		key,
		value = $bindable(),
		options,
	}: {
		key: string;
		value: T;
		options: T[] | { key: string; value: T }[];
	} = $props();
</script>

<div class="frow-2 bg-white wrapped flex-grow min-w-0">
	<div class="editor-label">{key}</div>
	<Separator />
	<div class="relative flex-grow -mx-2 px-2 min-w-0">
		<Select bind:value {options} />
	</div>
</div>
