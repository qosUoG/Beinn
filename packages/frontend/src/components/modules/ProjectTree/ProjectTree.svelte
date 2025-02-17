<script lang="ts">
	import { cn } from "$components/utils";
	import { gstore } from "$states/global.svelte";
</script>

<div class="col-1 w-52 h-full min-h-0">
	<!-- <div class="wrapped bg-slate-200">Project</div> -->
	<div class="h-full overflow-y-scroll w-full p-2 bg-slate-200 rounded">
		<div class="col-1">
			<!-- TODO nested drectory {#each Object.entries(project.directory.dirs) as dir}
            {/each} -->
			{#each gstore.workspace.directory.files as file}
				<button
					class={cn(
						"py-0.5 px-1 bg-slate-50 rounded break-words w-full border border-slate-50",
						gstore.experiment.path === file
							? "border border-green-500 bg-green-200"
							: "'"
					)}
					onclick={() => {
						gstore.experiment.path = file;
					}}>
					{file}
				</button>
			{/each}
		</div>
	</div>
</div>
