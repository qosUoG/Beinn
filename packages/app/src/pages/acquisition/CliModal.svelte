<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
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
</script>

<div
	class="absolute top-0 left-0 w-full h-full z-1000 flex justify-center items-center backdrop-blur-2xl">
	<div class="bg-slate-800 rounded w-xl h-3/4">
		<div class="fcol-2 p-2 min-h-0 h-full w-full" {@attach clickoutside}>
			<div
				class="overflow-y-scroll fcol text-white min-h-0 grow scrollbar-slate-300 w-full"
				bind:this={large}
				onscroll={() => {
					experiment_controller.experiment!.cli.large_scroll_height =
						large!.scrollTop;
				}}>
				{#each experiment_controller.experiment!.cli.logs.entries as entry}
					<div
						class="text-white whitespace-pre-wrap break-all grow font-mono text-[11px] max-w-full">
						{entry}
					</div>
				{/each}
			</div>
			<div
				class="text-white frow font-mono text-[11px] whitespace-pre-wrap break-all
					">
				<div
					class="text-white font-mono text-[11px] text-nowrap whitespace-break-spaces min-w-7">
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
					role={"input of repl"}>
				</div>
			</div>
		</div>
	</div>
</div>
