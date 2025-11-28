<script lang="ts">
	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import {
		ChevronsDown,
		Maximize2,
		SquareTerminal,
		Terminal,
	} from "@lucide/svelte";
	import { onMount } from "svelte";
	import CliModal from "./CliModal.svelte";

	import Cli from "$components/cli/Cli";

	const clickoutside = getClickOutsideAttachment(() => {
		show_cli = false;
	});

	let show_cli = $state(false);
</script>

<div class=" grow bg-slate-800 rounded p-2 relative">
	<div class="absolute top-1 right-1 frow-2">
		<button
			class=" rounded border border-slate-200 icon-btn-sm text-white"
			onclick={(e) => {
				show_cli = !show_cli;
				e.stopPropagation();
			}}
		>
			<Maximize2 />
		</button>
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
	</div>
	<div class="fcol w-full min-h-0 mt-8">
		<Cli.Log bind:cli={experiment_controller.experiment!.cli} />

		{#if experiment_controller.experiment!.state === "looping" || experiment_controller.experiment!.state.startsWith("paus")}
			<div
				class="text-white font-mono text-[11px] whitespace-pre-wrap ml-1 mb-1.5 self-end"
			>
				{`>>>`}<Cli.Input
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
