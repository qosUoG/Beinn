<script lang="ts">
	import Cli from "$components/cli/Cli";
	import { cn } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { ChevronsDown } from "@lucide/svelte";

	let { clickoutside }: { clickoutside: (e: HTMLDivElement) => void } =
		$props();
</script>

<div
	class="absolute top-0 left-0 w-full h-full z-1000 flex justify-center items-center backdrop-blur-2xl"
>
	<div class="bg-slate-800 rounded w-xl h-3/4">
		<div
			class="fcol-2 p-2 min-h-0 h-full w-full relative"
			{@attach clickoutside}
		>
			<button
				class={cn(
					"absolute top-0 left-0 rounded border border-slate-200 ml-2 mt-2",
					experiment_controller.experiment!.cli.follow_scroll
						? "bg-slate-200 text-slate-50 "
						: "",
				)}
				onclick={() => {
					experiment_controller.experiment!.cli.follow_scroll =
						!experiment_controller.experiment!.cli.follow_scroll;
				}}
			>
				<div
					class={cn(
						"icon-btn-sm ",
						experiment_controller.experiment!.cli.follow_scroll
							? "animate-pulse text-slate-800"
							: "text-slate-200",
					)}
				>
					<ChevronsDown />
				</div>
			</button>

			<Cli.Log bind:cli={experiment_controller.experiment!.cli} />
			{#if experiment_controller.experiment!.state === "looping" || experiment_controller.experiment!.state.startsWith("paus")}
				<div
					class="text-white frow font-mono text-[11px] whitespace-pre-wrap break-all
					"
				>
					<div
						class="text-white font-mono text-[11px] text-nowrap whitespace-break-spaces min-w-7"
					>
						{`>>> `}
					</div>
					<Cli.Input
						bind:cli={experiment_controller.experiment!.cli}
						onEnter={() => {
							experiment_controller.experiment!.interpret();
						}}
					/>
				</div>
			{/if}
		</div>
	</div>
</div>
