<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import type { ShellEntry } from "$controllers/log.svelte";
	import {
		ChevronLeft,
		ChevronDown,
		Terminal,
		Folder,
		TriangleAlert,
		CalendarClock,
	} from "@lucide/svelte";
	let { entry }: { entry: ShellEntry } = $props();

	let open = $state(true);

	let error = $derived(
		entry.code === null || entry.code > 0 || entry.err !== ""
	);
</script>

<div
	class={cn(
		"fcol  rounded px-2 ",
		error ? "bg-red-100" : "bg-slate-200",
		open ? "pb-2" : ""
	)}>
	<button
		class=" frow-2 justify-between items-center"
		onclick={(e) => {
			open = !open;
			e.stopPropagation();
		}}>
		<div class="frow-2 items-center">
			{#if error}
				<span class="icon-btn-sm text-red-600">
					<TriangleAlert />
				</span>
			{/if}

			<div class="py-2 text-ellipsis">
				{entry.description}
			</div>
		</div>
		{#if !open}
			<span class="icon-btn-sm">
				<ChevronLeft />
			</span>
		{:else}
			<span class="icon-btn-sm">
				<ChevronDown />
			</span>
		{/if}
	</button>

	{#if open}
		<div class="fcol-1">
			<div class="frow-2 items-center">
				<span class="icon-btn-sm">
					<CalendarClock />
				</span>
				{new Date(entry.timestamp).toLocaleString()}
			</div>

			<div class="frow-2 items-center">
				<span class="icon-btn-sm">
					<Folder />
				</span>
				{entry.cwd}
			</div>
			<div class="fcol-1 bg-slate-600 rounded">
				<div class="frow-2 items-center text-white rounded p-1">
					<span class="icon-btn-sm text-white">
						<Terminal />
					</span>
					{entry.command}
				</div>
				<div class="p-2 pt-0 fcol-1">
					{#each entry.std as { type, data }}
						<div class="text-white">{data}</div>
					{/each}
				</div>
			</div>
			<div>{entry.code}</div>
		</div>
	{/if}
</div>
