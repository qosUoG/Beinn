<script lang="ts">
	import Dependencies from "./dependency/Dependencies.svelte";
	import Equipments from "./equipment/Equipments.svelte";
	import Experiment from "./experiment/Experiment.svelte";
	import WorkspaceSelect from "./WorkspaceSelect.svelte";
</script>

<div class="grid grid-cols-3 h-full gap-4 p-2">
	<div class="fcol-2 h-full">
		<WorkspaceSelect />
		<Dependencies />
	</div>
	<Equipments />
	<Experiment />
</div>
