<script lang="ts">
	import BackendWsStatus from "$components/modules/BackendWsStatus.svelte";
	import Mode from "$components/modules/Mode.svelte";
	import ProjectPath from "$components/modules/ProjectPath.svelte";
	import ProjectTree from "$components/modules/ProjectTree/ProjectTree.svelte";

	import ActivateScript from "$components/modules/ActivateScript.svelte";
</script>

<div class="col-4 w-full h-full p-4">
	<div class="row-4 w-full items-stretch">
		<Mode />
		<ProjectPath />
		<BackendWsStatus />
	</div>
	<div class="row-4 h-full min-h-0 items-start">
		<ProjectTree />
		<ActivateScript />
	</div>
</div>
