<script lang="ts">
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { NotepadText, SquareTerminal } from "@lucide/svelte";
	import Note from "./Note.svelte";
	import { cn } from "$components/utils.svelte";
	import Cli from "./Cli.svelte";
</script>

{#if experiment_controller.experiment}
	<div class=" rounded grow frow items-start bg-slate-700 min-h-0 h-full">
		{#if experiment_controller.experiment.state === "ready"}
			{#if experiment_controller.experiment.note !== undefined}
				<div class="grid grid-rows-2 h-full rounded">
					<button
						class={cn(
							" rounded-tl ",
							experiment_controller.experiment.sidetab_showing ===
								"notes"
								? "bg-slate-700"
								: "bg-slate-200"
						)}
						onclick={() => {
							experiment_controller.experiment!.sidetab_showing =
								"notes";
						}}>
						<div
							class={cn(
								"icon-btn-sm ",
								experiment_controller.experiment
									.sidetab_showing === "notes"
									? "text-white"
									: ""
							)}>
							<NotepadText />
						</div>
					</button>
					<button
						class={cn(
							" rounded-bl ",
							experiment_controller.experiment.sidetab_showing ===
								"cli"
								? "bg-slate-700"
								: "bg-slate-200"
						)}
						onclick={() => {
							experiment_controller.experiment!.sidetab_showing =
								"cli";
						}}>
						<div
							class={cn(
								"icon-btn-sm ",
								experiment_controller.experiment
									.sidetab_showing === "cli"
									? "text-white"
									: ""
							)}>
							<SquareTerminal />
						</div>
					</button>
				</div>
				{#if experiment_controller.experiment.sidetab_showing === "notes"}
					<Note />
				{:else}
					<Cli />
				{/if}
			{:else}
				<Cli />
			{/if}
		{/if}
	</div>
{/if}
