<script lang="ts">
	import Editor from "$components/modules/Editor/Editor.svelte";
	import EquipmentList from "$components/modules/List/EquipmentList.svelte";
	import ExperimentList from "$components/modules/List/ExperimentList.svelte";
	import DependencyList from "$components/modules/List/DependencyList.svelte";
</script>

<div class="grid grid-cols-5 min-h-0 gap-4 h-full">
	<DependencyList />
	<EquipmentList />
	<ExperimentList />
	<Editor />
</div>
