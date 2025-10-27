<script lang="ts">
	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import { Pencil, PencilOff } from "@lucide/svelte";
	import { tick } from "svelte";

	let open = $state(false);

	const clickoutside = getClickOutsideAttachment(() => {
		open = false;
	});
</script>

{#if workspace_controller.status === "ready"}
	<div class=" bg-white rounded min-h-[24px]">
		<div
			{@attach clickoutside}
			class=" py-0.5 px-1 frow text-center relative">
			{#if open}
				<div
					class="bg-slate-200 absolute bottom-0 left-0 w-full rounded border p-2">
					{#each experiment_controller.imports as { cls, module }}
						<button
							class={cn(
								"text-slate-400 wrapped  w-full",
								experiment_controller.cls === cls &&
									experiment_controller.module === module
									? "bg-slate-700 text-slate-500"
									: "hover:bg-slate-300"
							)}
							onclick={async () => {
								if (
									experiment_controller.cls === cls &&
									experiment_controller.module === module
								)
									return;

								experiment_controller.module = module;
								experiment_controller.cls = cls;

								open = false;
								await tick();
								await experiment_controller.loadExperiment();
							}}>
							from
							<span
								class={cn(
									" font-semibold",
									experiment_controller.cls === cls &&
										experiment_controller.module === module
										? "text-white"
										: "text-slate-950"
								)}>
								{module}
							</span>
							import
							<span
								class={cn(
									" font-semibold",
									experiment_controller.cls === cls &&
										experiment_controller.module === module
										? "text-white"
										: "text-slate-950"
								)}>
								{cls}
							</span>
						</button>
					{:else}
						<span
							class="text-slate-400 wrapped italic select-none cursor-default">
							No available imports ...
						</span>
					{/each}
				</div>
			{/if}

			{#if experiment_controller.editable}
				<button
					class="w-full frow items-center"
					onclick={() => {
						open = true;
					}}>
					<div class="flex-grow">
						{#if experiment_controller.cls && experiment_controller.module}
							from
							<span class="text-slate-950 font-semibold">
								{experiment_controller.module}
							</span>
							import
							<span class="text-slate-950 font-semibold">
								{experiment_controller.cls}
							</span>
						{:else}
							<span class="text-slate-400 italic"
								>Select experiment ...</span>
						{/if}
					</div>

					{#if experiment_controller.experiment}
						<span class=" icon-btn-sm text-slate-400">
							<Pencil />
						</span>
					{/if}
				</button>
			{:else}
				<span class="w-full frow items-center">
					<div class="flex-grow">
						{#if experiment_controller.cls && experiment_controller.module}
							from
							<span class="text-slate-950 font-semibold">
								{experiment_controller.module}
							</span>
							import
							<span class="text-slate-950 font-semibold">
								{experiment_controller.cls}
							</span>
						{:else}
							<span class="text-slate-400 italic"
								>Select experiment ...</span>
						{/if}
					</div>
					{#if experiment_controller.experiment}
						<span class=" icon-btn-sm text-slate-400">
							<PencilOff />
						</span>
					{/if}
				</span>
			{/if}
		</div>
	</div>
{/if}
