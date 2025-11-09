<script lang="ts">
	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { ChevronsDown, SquareTerminal, Terminal } from "@lucide/svelte";
	import { onMount, tick } from "svelte";
	import CliModal from "./CliModal.svelte";

	const clickoutside = getClickOutsideAttachment(() => {
		show_cli = false;
	});
	let editable: HTMLDivElement | undefined = $state(undefined);

	async function keyDownHandler(e: KeyboardEvent) {
		switch (e.key) {
			case "Enter":
				if (!e.shiftKey && !e.ctrlKey) {
					e.preventDefault();
					experiment_controller.experiment!.interpret();
				}
				return;
			case "ArrowDown": {
				e.preventDefault();
				experiment_controller.experiment!.cli.next();
				return;
			}
			case "ArrowUp": {
				e.preventDefault();
				experiment_controller.experiment!.cli.prev();
				return;
			}
			case "Tab": {
				e.preventDefault();
				const range = document.createRange();
				const selection = window.getSelection()!;
				const offset = selection.getRangeAt(0).startOffset;
				experiment_controller.experiment!.cli.command =
					experiment_controller.experiment!.cli.command.slice(
						0,
						offset
					) +
					"    " +
					experiment_controller.experiment!.cli.command.slice(offset);

				await tick();

				range.setStart(editable!.childNodes[0], 4 + offset);
				range.collapse(true);

				selection.removeAllRanges();
				selection.addRange(range);

				return;
			}
		}
	}

	let show_cli = $state(false);

	let small: HTMLDivElement | undefined = $state(undefined);

	onMount(() => {
		if (small)
			small.scrollTop =
				experiment_controller.experiment!.cli.small_scroll_height;
	});
	$effect(() => {
		if (small === undefined) return;

		experiment_controller.experiment!.cli.command;
		experiment_controller.experiment!.cli.logs.entries;

		if (experiment_controller.experiment!.cli.follow_scroll) {
			experiment_controller.experiment!.cli.small_scroll_height =
				small.scrollHeight;
			small.scrollTop = small.scrollHeight;
		}
	});
</script>

<div class="frow-1 grow bg-slate-800 rounded p-1 relative">
	<div class="absolute top-0 left-0 fcol justify-between h-full">
		<button
			class={cn(
				"rounded border border-slate-200 ml-1 mt-1",
				experiment_controller.experiment!.cli.follow_scroll
					? "bg-slate-200 text-slate-50 "
					: ""
			)}
			onclick={() => {
				experiment_controller.experiment!.cli.follow_scroll =
					!experiment_controller.experiment!.cli.follow_scroll;
			}}>
			<div
				class={cn(
					"icon-btn-sm ",
					experiment_controller.experiment!.cli.follow_scroll
						? "animate-pulse text-slate-800"
						: "text-slate-200"
				)}>
				<ChevronsDown />
			</div>
		</button>
		<div
			class="text-white font-mono text-[11px] whitespace-pre-wrap ml-1 mb-1.5 self-end">
			{`>>>`}
		</div>
	</div>
	<div class="fcol w-full min-h-0 ml-8">
		<button
			class=" min-h-0 w-full rounded grow"
			onclick={(e) => {
				show_cli = !show_cli;
				e.stopPropagation();
			}}>
			<div
				bind:this={small}
				class="overflow-y-scroll fcol text-white min-h-0 h-full scrollbar-slate-300 w-full"
				onscroll={() => {
					experiment_controller.experiment!.cli.small_scroll_height =
						small!.scrollTop;
				}}>
				{#each experiment_controller.experiment!.cli.logs.entries as entry}
					<div
						class="text-white text-left font-mono whitespace-pre-wrap break-all text-[11px]">
						{entry}
					</div>
				{/each}
			</div>
		</button>

		<div
			contenteditable="plaintext-only"
			bind:innerText={experiment_controller.experiment!.cli.command}
			bind:this={editable}
			class=" text-white font-mono text-[11px] whitespace-break-spaces break-all min-h-4 grow focus:outline-none"
			spellcheck="false"
			autocapitalize="off"
			onkeydown={keyDownHandler}
			role={"input of repl"}>
		</div>
	</div>
</div>

{#if show_cli}
	<CliModal {clickoutside} />
{/if}
