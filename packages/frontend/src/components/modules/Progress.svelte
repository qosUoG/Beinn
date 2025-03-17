<script lang="ts">
	import {
		ExperimentStatus,
		getExperimentStatus,
		type CreatedExperiment,
	} from "qoslab-shared";

	let { experiment }: { experiment: CreatedExperiment } = $props();
</script>

{#if getExperimentStatus(experiment) === ExperimentStatus.Started || getExperimentStatus(experiment) === ExperimentStatus.Paused || getExperimentStatus(experiment) === ExperimentStatus.Completed}
	{experiment.loop_count}
{:else}
	<div class="flex-grow"></div>
{/if}
