<script lang="ts">
	import Mode from "$components/modules/Mode.svelte";
	import ProjectPath from "$components/modules/ProjectPath.svelte";

	import { gstore } from "$states/global.svelte";

	import Config from "$pages/Config.svelte";
	import Experiments from "$pages/Experiments.svelte";
</script>

<div class="col-4 w-full h-full p-4">
	<div class="row-4 w-full items-stretch">
		<Mode />
		<ProjectPath />
	</div>
	{#if gstore.mode === "CONFIG"}
		<Config />
	{:else if gstore.mode === "EXPERIMENTS"}
		<Experiments />
	{/if}
</div>
