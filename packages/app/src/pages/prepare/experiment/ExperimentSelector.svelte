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
	<div class="frow items-center bg-white rounded min-h-[24px]">
		<div
			{@attach clickoutside}
			class=" py-0.5 px-1 flex-grow w-fit border-slate-400 text-center relative">
			{#if open}
				<div
					class="bg-white absolute bottom-0 left-0 w-full rounded border">
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
						<button
							onclick={() => {
								open = false;
							}}
							class="text-slate-400 wrapped italic select-none cursor-default">
							No available imports ...
						</button>
					{/each}
				</div>
			{/if}
			{#if experiment_controller.editable}
				<button
					class="w-full"
					onclick={() => {
						open = true;
					}}>
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
				</button>
			{:else}
				<span class="w-full">
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
				</span>
			{/if}
		</div>

		{#if experiment_controller.experiment}
			{#if experiment_controller.editable}
				<span class=" icon-btn-sm text-slate-400">
					<Pencil />
				</span>
			{:else}
				<span class=" icon-btn-sm">
					<PencilOff />
				</span>
			{/if}
		{/if}
	</div>
{/if}
