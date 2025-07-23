<script lang="ts">
	import { controller } from "../../../controllers/app_controller.svelte";
	import type { Dependency } from "../../../controllers/dependency_controller.svelte";

	let { dependency }: { dependency: Dependency } = $props();
</script>

<div class="bg-slate-100 rounded p-1 flex flex-col gap-0.5">
	<div class="flex items-center w-full justify-between">
		<div class=" text-slate-950 font-medium wrapped px-0">
			{dependency.name}
		</div>
		<div class="self-stretch">
			<button
				aria-label="Remove dependency"
				class="bg-red-600 h-full aspect-square rounded flex items-center justify-center hover:bg-red-700 transition-colors -translate-x-1/2"
				onclick={async () => {
					controller.uninstallDependency(dependency.name);
				}}>
				<span class="icon-[lucide--x] text-red-100"></span>
			</button>
		</div>
	</div>
	{#if dependency.source.type === "git"}
		<div class="text-slate-950/75">
			Git: {dependency.source.git}
		</div>
		<div class="text-slate-950/75">
			Branch: {dependency.source.branch}
		</div>
		<div class="text-slate-950/75">
			Subdirectory: {dependency.source.subdirectory}
		</div>
	{:else if dependency.source.type === "path"}
		<div class="text-slate-950/75">
			Path: {dependency.source.path}
		</div>
		<div class="text-slate-950/75">
			{dependency.source.editable ? "Editable" : "Not editable"}
		</div>
	{:else if dependency.source.type === "pip"}
		<div class="text-slate-950/75">
			Pip: {dependency.fullname}
		</div>
	{/if}
</div>
