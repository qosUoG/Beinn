<script lang="ts">
	import { cn } from "$components/utils";
	import type { Booleanish, HTMLInputTypeAttribute } from "svelte/elements";

	let {
		class: clazz,
		spellcheck = "true",
		type,
		value = $bindable(),
	}: {
		class?: string;
		spellcheck?: Booleanish;
		type: HTMLInputTypeAttribute;
		value: any;
	} = $props();
</script>

<input {spellcheck} class={cn("focus:outline-none", clazz)} {type} bind:value />
