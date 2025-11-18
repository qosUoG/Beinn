<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { ChevronsDown } from "@lucide/svelte";
	import { onMount, tick } from "svelte";

	let { clickoutside }: { clickoutside: (e: HTMLDivElement) => void } =
		$props();

	let large: HTMLDivElement | undefined = $state(undefined);
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
						offset,
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

	onMount(() => {
		if (large)
			large.scrollTop =
				experiment_controller.experiment!.cli.large_scroll_height;
	});
	$effect(() => {
		if (large === undefined) return;

		experiment_controller.experiment!.cli.command;
		experiment_controller.experiment!.cli.logs.entries;

		if (experiment_controller.experiment!.cli.follow_scroll) {
			experiment_controller.experiment!.cli.large_scroll_height =
				large.scrollHeight;
			large.scrollTop =
				experiment_controller.experiment!.cli.large_scroll_height;
		}
	});

	let onCli = $state(false);
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

			<div
				class="overflow-y-scroll fcol text-white min-h-0 grow scrollbar-slate-300 w-full pt-10"
				bind:this={large}
				onmouseenter={() => {
					onCli = true;
				}}
				onmouseleave={() => {
					onCli = false;
				}}
				role={"cli"}
				onwheel={() => {
					experiment_controller.experiment!.cli.large_scroll_height =
						large!.scrollTop;
					if (onCli)
						experiment_controller.experiment!.cli.follow_scroll = false;
				}}
			>
				{#each experiment_controller.experiment!.cli.logs.entries as entry}
					<div
						class="text-white whitespace-pre-wrap break-all font-mono text-[11px] max-w-full h-fit"
					>
						{entry}
					</div>
				{/each}
			</div>
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
					<div
						contenteditable="plaintext-only"
						bind:innerText={
							experiment_controller.experiment!.cli.command
						}
						bind:this={editable}
						class=" text-white font-mono text-[11px] whitespace-break-spaces break-all min-h-4 grow focus:outline-none"
						spellcheck="false"
						autocapitalize="off"
						onkeydown={keyDownHandler}
						role={"input of repl"}
					></div>
				</div>
			{/if}
		</div>
	</div>
</div>
