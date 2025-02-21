<script lang="ts">
	import Mode from "$components/modules/Mode.svelte";
	import ProjectPath from "$components/modules/ProjectPath.svelte";

	import Editor from "$components/modules/Editor.svelte";
	import EquipmentList from "$components/modules/EquipmentList.svelte";
	import ExperimentList from "$components/modules/ExperimentList.svelte";
</script>

<div class="col-4 w-full h-full p-4">
	<div class="row-4 w-full items-stretch">
		<Mode />
		<ProjectPath />
	</div>
	<!-- <div class="row-4 h-full min-h-0 items-start">
		<ProjectTree />
		<ActivateScript />
	</div> -->
	<div class="grid grid-cols-4 min-h-0 gap-4 h-full">
		<EquipmentList />
		<ExperimentList />

		<Editor />
	</div>
</div>
