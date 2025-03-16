<script lang="ts">
	import {
		ExperimentStatus,
		getExperimentStatus,
		type Experiment,
	} from "qoslab-shared";

	let { experiment }: { experiment: Extract<Experiment, { created: true }> } =
		$props();
</script>

{#if getExperimentStatus(experiment) === ExperimentStatus.Started || getExperimentStatus(experiment) === ExperimentStatus.Paused || getExperimentStatus(experiment) === ExperimentStatus.Completed}
	{experiment.loop_count}
{:else}
	<div class="flex-grow"></div>
{/if}
