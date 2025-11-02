<script lang="ts">
	import { getClickOutsideAttachment } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { SquareTerminal, Terminal } from "@lucide/svelte";

	const clickoutside = getClickOutsideAttachment(() => {
		show_cli = false;
	});

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
				experiment_controller.experiment!.cli.command += "    ";
				return;
			}
		}
	}

	let show_cli = $state(false);
</script>

<button
	class="frow-2 p-1 min-h-0 h-full w-full"
	onclick={(e) => {
		show_cli = !show_cli;
		e.stopPropagation();
	}}>
	<div class="icon-btn-sm rounded bg-slate-200">
		<SquareTerminal />
	</div>
	<div
		class="overflow-y-scroll fcol text-white min-h-0 h-full scrollbar-slate-300 w-full">
		{#each experiment_controller.experiment!.cli.logs.entries as entry}
			<div class="text-white text-left">
				{entry}
			</div>
		{/each}
	</div>
</button>

{#if show_cli}
	<div
		class="absolute top-0 left-0 w-full h-full z-1000 flex justify-center items-center backdrop-blur-2xl">
		<div class="bg-slate-700 rounded w-xl h-3/4">
			<div
				class="fcol-2 p-2 min-h-0 h-full w-full"
				{@attach clickoutside}>
				<div
					class="overflow-y-scroll fcol text-white min-h-0 grow scrollbar-slate-300 w-full">
					{#each experiment_controller.experiment!.cli.logs.entries as entry}
						<div class="text-white">
							{entry}
						</div>
					{/each}
				</div>
				<div
					class="w-full bg-slate-200 rounded p-2 frow-2 items-center">
					<div class="icon-btn-sm">
						<Terminal />
					</div>
					<textarea
						onkeydown={keyDownHandler}
						class=" resize-none outline-none focus:outline-none grow scrollbar-slate-400 font-mono h-12"
						spellcheck="false"
						autocomplete="off"
						autocapitalize="off"
						bind:value={
							experiment_controller.experiment!.cli.command
						}></textarea>
				</div>
			</div>
		</div>
		<!-- <div class="frow-2 p-1 min-h-0 h-full w-full">
            <div class="icon-btn-sm rounded bg-slate-200">
                <SquareTerminal />
            </div>
            <input
                class="w-full bg-slate-200 wrapped"
                bind:value={input}
                autocapitalize="off"
                autocomplete="off"
                autocorrect="off"
                spellcheck="false"
                onkeydown={keyDownHandler} />
        </div> -->
	</div>
{/if}
