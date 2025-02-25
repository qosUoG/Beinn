<script lang="ts">
	import Input from "$components/reuseables/Input.svelte";
	import { clickoutside, cn } from "$components/utils.svelte";
	import Cancel from "$icons/Cancel.svelte";
	import Disk from "$icons/Disk.svelte";
	import Plus from "$icons/Plus.svelte";
	import Tick from "$icons/Tick.svelte";
	import { gstore } from "$states/global.svelte";

	$inspect(gstore.workspace.directory.files.length);

	let add_dependency_modal_is_showing = $state(false);
	let temp_dependency_path = $state("");
</script>

<div class="container col-2 bg-slate-200">
	<div class="col-2">
		<div class="row justify-between items-center">
			<div class="title bg-white wrapped self-start">Project</div>
			<button
				class="icon-btn-sm slate"
				onclick={(e) => {
					e.stopPropagation();
					add_dependency_modal_is_showing = true;
				}}><Plus /></button>
		</div>

		{#if gstore.workspace.directory.files.length > 0}
			<div class="col-1">
				<!-- TODO nested drectory {#each Object.entries(workspace.directory.dirs) as dir} {/each} -->
				{#each gstore.workspace.directory.files.filter( (f) => f.endsWith(".py") ) as file}
					<div class={cn(" bg-white  break-words w-full wrapped")}>
						{file}
					</div>
				{/each}
			</div>
		{/if}

		{#if gstore.workspace.dependencies.length > 0}
			<div class="col-1">
				{#each gstore.workspace.dependencies as dependency}
					<div class="title bg-white wrapped self-start">
						{dependency}
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

{#if add_dependency_modal_is_showing}
	<div class="modal">
		<div
			class="container bg-white shadow-xl w-128 col-4"
			use:clickoutside
			onoutsideclick={() => (add_dependency_modal_is_showing = false)}>
			<div class="heading text-center">Add Dependency</div>
			<div class="row-1">
				<div
					class="w-fit wrapped text-nowrap bg-slate-200 flex items-center">
					Path
				</div>
				<Input
					spellcheck="false"
					class="flex-grow wrapped bg-slate-200"
					type="text"
					bind:value={temp_dependency_path} />
			</div>
			<div class="grid grid-cols-2 gap-2">
				<button
					class="red wrapped flex justify-center"
					onclick={() => {
						temp_dependency_path = "";
						add_dependency_modal_is_showing = false;
					}}>
					<div class="icon-btn red">
						<Cancel />
					</div>
				</button>
				<button
					class="green wrapped flex justify-center"
					onclick={() => {
						temp_dependency_path = "";
						add_dependency_modal_is_showing = false;
					}}>
					<div class="icon-btn green"><Disk /></div>
				</button>
			</div>
		</div>
	</div>
{/if}
