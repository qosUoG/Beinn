<script lang="ts">
	import { equipment_controller } from "$controllers/equipment.svelte";

	let { equipment = $bindable() }: { equipment: Instance } = $props();

	import {
		ChevronDown,
		ChevronRight,
		ChevronsLeftRightEllipsis,
		FolderSync,
		LoaderCircle,
		Trash2,
	} from "@lucide/svelte";

	import { cn } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import ParamList from "$components/param/ParamList.svelte";

	import type { Instance } from "$controllers/_ee.svelte";
	import { tick } from "svelte";
</script>

<div class="bg-white rounded fcol-1 p-1">
	<div class="flex items-center w-full justify-between">
		{#if experiment_controller.editable}
			<input
				autocomplete="off"
				autocorrect="off"
				autocapitalize="off"
				spellcheck="false"
				class={cn(
					"  font-light text-slate-950 flex items-center px-1 text-sm",
					equipment.name === equipment.temp_name ? "" : "text-red-500"
				)}
				bind:value={
					() => equipment.temp_name,
					(value) => {
						equipment.temp_name = value;

						// Assign to name as well if not already used
						if (
							equipment_controller.equipment_names.includes(value)
						)
							return;

						const old_name = equipment.name;
						equipment.name = value;

						tick().then(() => {
							equipment_controller.save();

							// Change equipment name in experiment params
							if (experiment_controller.experiment === undefined)
								return;

							for (const param of Object.values(
								experiment_controller.experiment.params
							)) {
								if (
									param.type === "instance.equipment" &&
									param.value === old_name
								)
									param.value = value;
								else if (!("type" in param)) {
									for (const p of Object.values(param)) {
										if (
											p.type === "instance.equipment" &&
											p.value === old_name
										)
											p.value = value;
									}
								}
							}

							tick().then(() => {
								experiment_controller.save();
							});
						});
					}
				} />
		{:else}<div
				class="  font-light text-slate-950 flex items-center px-1 text-sm">
				{equipment.name}
			</div>
		{/if}

		<div class="frow-1">
			<button
				aria-label={`REPL ${equipment.name}`}
				class={cn(
					" icon-btn-sm text-white ",
					experiment_controller.editable
						? " bg-green-500"
						: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
				)}
				onclick={async () => {
					if (experiment_controller.editable)
						await equipment_controller.startREPL(equipment);
				}}>
				<ChevronsLeftRightEllipsis />
			</button>
			{#if equipment.reloading}
				<div class="icon-btn-sm bg-blue-600">
					<div class="text-white animate-spin">
						<LoaderCircle />
					</div>
				</div>
			{:else}
				<button
					aria-label={`Reload ${equipment.name}`}
					class={cn(
						" icon-btn-sm text-white ",
						experiment_controller.editable
							? "bg-blue-600"
							: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
					)}
					onclick={() => {
						if (experiment_controller.editable) equipment.reload();
					}}>
					<FolderSync />
				</button>
			{/if}

			<button
				aria-label={`Remove ${equipment.name}`}
				class={cn(
					" icon-btn-sm text-white ",
					experiment_controller.editable
						? "bg-red-600"
						: "bg-slate-300 cursor-not-allowed *:cursor-not-allowed **:cursor-not-allowed"
				)}
				onclick={() => {
					if (experiment_controller.editable)
						equipment_controller.remove(equipment.name);
				}}>
				<Trash2 />
			</button>
		</div>
	</div>
	<div>
		<div
			class={cn(
				"grid grid-cols-2 border-2 border-slate-800 bg-slate-300 rounded-t p-0.5",
				equipment.param_opens ? "" : "rounded-b"
			)}>
			<button
				class={cn(
					"frow items-center   pr-4 rounded-tr rounded-tl h-full"
				)}
				onclick={() => {
					equipment.param_opens = !equipment.param_opens;
				}}>
				<span class="h-3">
					{#if !equipment.param_opens}
						<ChevronRight strokeWidth="3px" />
					{:else}
						<ChevronDown strokeWidth="3px" />
					{/if}
				</span>
				<div class="  wrapped px-0">Params</div>
			</button>
		</div>

		<ParamList
			param_opens={equipment.param_opens}
			bind:composite_opens={equipment.composite_opens}
			bind:params={equipment.params}
			saveFn={async () => {
				await equipment_controller.save();
			}} />
	</div>
</div>
