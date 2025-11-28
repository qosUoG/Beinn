<script lang="ts">
	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { ChevronsDown, Maximize2 } from "@lucide/svelte";

	import CliModal from "./CliModal.svelte";

	import Cli from "$components/cli/Cli";

	const clickoutside = getClickOutsideAttachment(() => {
		show_cli = false;
	});

	let show_cli = $state(false);
</script>

<div class="  bg-slate-800 rounded relative h-full row-span-1">
	<div class="absolute top-1 right-4 frow-2">
		<button
			class={cn(
				"rounded border border-slate-200 icon-btn-sm ",
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
					" ",
					experiment_controller.experiment!.cli.follow_scroll
						? "animate-pulse text-slate-800"
						: "text-slate-200",
				)}
			>
				<ChevronsDown />
			</div>
		</button>
		<button
			class=" rounded border border-slate-200 bg-slate-200 icon-btn-sm"
			onclick={(e) => {
				show_cli = !show_cli;
				e.stopPropagation();
			}}
		>
			<Maximize2 />
		</button>
	</div>
	<div class="fcol w-full h-full">
		<Cli.Log
			bind:cli={experiment_controller.experiment!.cli}
			class="pl-2 pt-8"
		/>

		{#if experiment_controller.experiment!.state === "looping" || experiment_controller.experiment!.state.startsWith("paus")}
			<div
				class="text-white font-mono text-[11px] whitespace-pre-wrap frow"
			>
				{`>>> `}<Cli.Input
					bind:cli={experiment_controller.experiment!.cli}
					onEnter={() => {
						experiment_controller.experiment!.interpret();
					}}
				/>
			</div>
		{/if}
	</div>
</div>

{#if show_cli}
	<CliModal {clickoutside} />
{/if}
