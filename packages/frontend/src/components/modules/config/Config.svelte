<script lang="ts">
	import Editor from "$components/modules/config/editor/Editor.svelte";
	import EquipmentList from "$components/modules/config/list/EquipmentList.svelte";
	import ExperimentList from "$components/modules/config/list/ExperimentList.svelte";
	import DependencyList from "$components/modules/config/list/DependencyList.svelte";
</script>

<div class="w-full overflow-x-scroll">
	<div class="grid grid-cols-5 min-h-0 min-w-[1300px] gap-4 h-full w-full">
		<DependencyList />
		<EquipmentList />
		<ExperimentList />
		<Editor />
	</div>
</div>
