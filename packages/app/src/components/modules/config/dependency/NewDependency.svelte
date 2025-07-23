<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import LabelField from "$components/reuseables/LabelField.svelte";
	import DivField from "$components/reuseables/DivField.svelte";
	import {
		dependencies,
		type DependencySource,
		type PathSource,
	} from "$controllers/DependencyController.svelte";
	import { workspace } from "$controllers/WorkspaceController.svelte";
	import { beinn_log_controller } from "$controllers/LogController.svelte";

	let source: DependencySource = $state({
		type: "pip",
		package: "",
	});
</script>

<div class="bg-slate-100 rounded p-1 fcol gap-1">
	<div class="title text-center wrapped relative">
		New Dependency
		<button
			class="absolute right-0 top-0 flex items-center h-full bg-blue-600 rounded aspect-square justify-center"
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
			<span class="icon-[lucide--plus] text-blue-100"></span>
		</button>
	</div>

	<DivField key="Type">
		<div class="grid grid-cols-3 w-full -my-1 -mr-2">
			<button
				class={cn(
					"border-r border-slate-300",
					source.type === "pip" ? "bg-slate-300" : ""
				)}
				onclick={() => {
					source = { type: "pip", package: "" };
				}}>pip</button>

			<button
				class={cn(
					"border-x border-slate-300",
					source.type === "git" ? "bg-slate-300" : ""
				)}
				onclick={() => {
					source = {
						type: "git",
						git: "",
						branch: "",
						subdirectory: "",
					};
				}}>git</button>

			<button
				class={cn(
					"border-l border-slate-300",
					source.type === "path" ? "bg-slate-300" : ""
				)}
				onclick={() => {
					source = { type: "path", path: "", editable: false };
				}}>path</button>
		</div>
	</DivField>

	{#if source.type === "pip"}
		<LabelField key="Package">
			<input bind:value={source.package} />
		</LabelField>
	{:else if source.type === "git"}
		<LabelField key="Git URL">
			<input bind:value={source.git} />
		</LabelField>
		<LabelField key="branch">
			<input bind:value={source.branch} />
		</LabelField>
		<LabelField key="Subdirectory">
			<input bind:value={source.subdirectory} />
		</LabelField>
	{:else if source.type === "path"}
		<LabelField key="Path">
			<input bind:value={source.path} />
		</LabelField>

		<DivField key="Type">
			<div class="grid grid-cols-2 w-full -my-1 -mr-2">
				<button
					class={cn(
						"border-r border-slate-300",
						source.editable ? "bg-slate-300" : ""
					)}
					onclick={() => {
						(source as PathSource).editable = true;
					}}>True</button>

				<button
					class={cn(
						"border-l border-slate-300",
						source.editable ? "" : "bg-slate-300"
					)}
					onclick={() => {
						(source as PathSource).editable = false;
					}}>False</button>
			</div>
		</DivField>
	{/if}
</div>
