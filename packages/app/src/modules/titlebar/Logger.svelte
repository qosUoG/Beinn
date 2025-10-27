<script lang="ts">
	import { getClickOutsideAttachment } from "$components/utils.svelte";
	import { log_controller } from "$controllers/log.svelte";
	import { ChevronLeft, ScrollText } from "@lucide/svelte";
	import ShellEntry from "./ShellEntry.svelte";

	const entry = $derived.by(() => {
		if (log_controller.log_entries.length === 0) return undefined;
		return log_controller.log_entries[
			log_controller.log_entries.length - 1
		];
	});

	let show_log = $state(false);

	const clickoutside = getClickOutsideAttachment(() => {
		show_log = false;
	});
</script>

<button
	class="h-full bg-slate-200 rounded w-72 flex items-center justify-between pr-1 z-1000"
	onclick={(e) => {
		show_log = true;
		e.stopPropagation();
	}}>
	{#if entry}
		{#if entry.type === "shell"}
			<div class="frow-2 items-center h-full">
				<div
					class="bg-slate-600 text-white rounded-l h-full px-1 text-[10px] flex items-center">
					SHELL
				</div>
				<div
					class="text-ellipsis overflow-hidden w-[212px] whitespace-nowrap">
					{entry.description}
				</div>
			</div>
		{:else if entry.type === "error"}
			<div class="frow-2 items-center h-full">
				<div
					class="bg-red-600 text-white rounded h-full px-1 text-[10px] flex items-center">
					ERROR
				</div>
				<div
					class="text-ellipsis overflow-hidden w-[212px] whitespace-nowrap">
					{entry.message}
				</div>
			</div>
		{/if}

		<div class="icon-btn-sm">
			<ScrollText />
		</div>
	{/if}
</button>

{#if show_log}
	<div
		class="h-screen w-screen backdrop-blur-lg absolute top-0 left-0 z-10000 flex items-center justify-center">
		<div
			{@attach clickoutside}
			class="bg-white scrollbar-slate-600 rounded w-144 h-3/4 p-4 fcol-2 overflow-y-scroll">
			{#each log_controller.log_entries as entry}
				{#if entry.type === "shell"}
					<ShellEntry {entry} />
				{:else if entry.type === "error"}
					<div class="frow-2 items-center">
						<div
							class="fcol items-center bg-slate-800 rounded-l py-1 px-2">
							<!-- <span class="icon-btn-sm">
					<CalendarClock />
				</span> -->
							<div class=" text-[10px] text-white">
								{new Date(entry.timestamp)
									.toLocaleString()
									.split(", ")[0]}
							</div>
							<div class=" text-[10px] text-white">
								{new Date(entry.timestamp)
									.toLocaleString()
									.split(", ")[1]}
							</div>
						</div>

						<!-- {#if error}
				<span class="icon-btn-sm text-red-600">
					<TriangleAlert />
				</span>
			{/if} -->

						<div class="py-2 text-ellipsis">
							{entry.message}
						</div>
					</div>
				{/if}
			{/each}
		</div>
	</div>
{/if}
