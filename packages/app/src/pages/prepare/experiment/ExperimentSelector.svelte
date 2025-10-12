<script lang="ts">
	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { Check } from "@lucide/svelte";

	let open = $state(false);

	const clickoutside = getClickOutsideAttachment(() => {
		open = false;
	});
</script>

<div class="frow items-center bg-white rounded">
	<div
		{@attach clickoutside}
		class=" py-0.5 px-1 flex-grow w-fit border-slate-400 text-center relative">
		{#if open}
			<div
				class="bg-white absolute bottom-0 left-0 w-full rounded border">
				{#each experiment_controller.imports as { cls, module }}
					{console.log(
						$state.snapshot(experiment_controller.imports)
					)}
					<button
						class={cn(
							"text-slate-400 wrapped  w-full",
							experiment_controller.cls === cls &&
								experiment_controller.module === module
								? "bg-slate-700 text-slate-500"
								: "hover:bg-slate-300"
						)}
						onclick={() => {
							experiment_controller.cls = cls;
							experiment_controller.module = module;
							open = false;
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
		<button
			class="w-full"
			onclick={() => {
				experiment_controller.updateImports();
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
				<span class="text-slate-400 italic">Select experiment ...</span>
			{/if}
		</button>
	</div>

	<button
		class=" icon-btn-sm"
		onclick={() => {
			experiment_controller.getParams();
		}}>
		<Check />
	</button>
</div>
