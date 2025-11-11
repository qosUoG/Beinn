<script lang="ts">
	import { Tab } from "$controllers/analysis.svelte";
	import { onMount } from "svelte";

	let { tab = $bindable() }: { tab: Tab } = $props();

	let plot_div: HTMLDivElement;

	onMount(() => {
		tab.mount(plot_div);
		return () => {
			tab.unmount();
		};
	});
</script>

<div class="p-1 rounded bg-white">
	<div bind:this={plot_div}></div>
</div>
