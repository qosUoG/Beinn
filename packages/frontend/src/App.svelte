<script lang="ts">
	import Mode from "$components/modules/Mode.svelte";
	import ProjectPath from "$components/modules/ProjectPath.svelte";

	import Editor from "$components/modules/Editor/Editor.svelte";
	import EquipmentList from "$components/modules/EquipmentList.svelte";
	import ExperimentList from "$components/modules/ExperimentList.svelte";
	import DependencyList from "$components/modules/DependencyList.svelte";
	import { gstore } from "$states/global.svelte";
	import ExperimentRunner from "$components/modules/ExperimentRunner.svelte";
</script>

<div class="col-4 w-full h-full p-4">
	<div class="row-4 w-full items-stretch">
		<Mode />
		<ProjectPath />
	</div>
	{#if gstore.mode === "CONFIG"}
		<div class="grid grid-cols-5 min-h-0 gap-4 h-full">
			<DependencyList />
			<EquipmentList />
			<ExperimentList />
			<Editor />
		</div>
	{:else if gstore.mode === "EXPERIMENT"}
		<ExperimentRunner />
	{/if}
</div>
