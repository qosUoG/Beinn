<script lang="ts">
	import type { Dependency } from "../../../controllers/dependency";

	let { dependency }: { dependency: Dependency } = $props();
</script>

<!-- <button></button> -->
<div class="bg-slate-100 rounded p-1 flex flex-col gap-1">
	<div class="flex items-center justify-between">
		<div class=" underline underline-offset-2">
			{dependency.name}
		</div>
		<div class="flex gap-1"></div>
	</div>
	{#if dependency.source.type === "git"}
		<div class="">
			Git: {dependency.source.git}
		</div>
		<div>
			Branch: {dependency.source.branch}
		</div>
		<div>
			Subdirectory: {dependency.source.subdirectory}
		</div>
	{:else if dependency.source.type === "path"}
		<div class="">
			Path: {dependency.source.path}
		</div>
		<div>
			{dependency.source.editable ? "Editable" : "Not editable"}
		</div>
	{:else if dependency.source.type === "pip"}
		<div class="">
			Pip: {dependency.fullname}
		</div>
	{/if}
</div>
