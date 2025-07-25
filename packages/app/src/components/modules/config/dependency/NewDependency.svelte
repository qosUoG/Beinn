<script lang="ts">
	import { cn } from "$components/utils.svelte";

	import {
		dependencies,
		type DependencySource,
	} from "$controllers/DependencyController.svelte";
	import { workspace } from "$controllers/WorkspaceController.svelte";
	import { beinn_log_controller } from "$controllers/LogController.svelte";
	import { Plus } from "@lucide/svelte";
	import InputField from "$components/fields/InputField.svelte";
	import TabSelect from "$components/fields/TabSelect.svelte";

	let source: DependencySource = $state({
		type: "pip",
		package: "",
	});
</script>

<div class="bg-slate-100 rounded p-1 pb-2 fcol h-[125px]">
	<div class="title text-center wrapped relative mb-1">
		New Dependency
		<button
			class="absolute right-0 top-0 flex items-center h-full bg-blue-600 rounded aspect-square justify-center icon-btn-sm text-white"
			aria-label="Add dependency"
			onclick={async () => {
				if (!workspace.path) {
					beinn_log_controller.append(
						"Cannot add dependency: No workspace path set."
					);
					return;
				}
				await dependencies.installDependency({
					path: workspace.path,
					source,
				});
				switch (source.type) {
					case "pip":
						source = { type: "pip", package: "" };
						break;
					case "git":
						source = {
							type: "git",
							git: "",
							branch: "",
							subdirectory: "",
						};
						break;
					case "path":
						source = {
							type: "path",
							path: "",
							editable: source.editable,
						};
						break;
				}
			}}>
			<Plus />
		</button>
	</div>
	{#snippet typeBoilerPlate(type: "pip" | "git" | "path")}
		<button
			class={cn(
				" border-slate-400   py-0.5",
				source.type === type ? "bg-slate-300 font-semibold " : ""
			)}
			onclick={() => {
				switch (type) {
					case "pip":
						source = { type: "pip", package: "" };
						break;
					case "git":
						source = {
							type: "git",
							git: "",
							branch: "",
							subdirectory: "",
						};
						break;
					case "path":
						source = { type: "path", path: "", editable: false };
						break;
				}
			}}>{type}</button>
	{/snippet}
	<div
		class="fcol *:border-1 *:border-slate-400 *:border-b-0 last:border-b-1 last:border-b-slate-400">
		<div class="frow items-stretch">
			<div class="min-w-16 px-1 h-full flex items-center">
				type<span class="text-red-500">*</span>
			</div>
			<div
				class="grid grid-cols-3 flex-grow *:border-l-1 *:border-slate-400">
				{@render typeBoilerPlate("pip")}
				{@render typeBoilerPlate("git")}
				{@render typeBoilerPlate("path")}
			</div>
		</div>

		{#if source.type === "pip"}
			<InputField label="package" bind:value={source.package} mandatory />
		{:else if source.type === "git"}
			<InputField
				label="url"
				bind:value={source.git}
				placeholder="https:// ... (without .git)"
				mandatory />
			<InputField label="branch" bind:value={source.branch} />
			<InputField label="subdirectory" bind:value={source.subdirectory} />
		{:else if source.type === "path"}
			<InputField label="path" bind:value={source.path} mandatory />
			<TabSelect
				label="editable"
				bind:value={source.editable}
				items={[
					{ key: "True", value: true },
					{ key: "False", value: false },
				]}
				mandatory />
		{/if}
	</div>
</div>
