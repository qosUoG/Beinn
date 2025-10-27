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
		Binary,
	} from "@lucide/svelte";
	let { entry }: { entry: ShellEntry } = $props();

	let open = $state(false);

	let error = $derived(
		entry.code === null || entry.code > 0 || entry.err !== ""
	);
</script>

<div
	class={cn(
		"fcol  rounded pr-2 ",
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
			<div
				class="fcol bg-slate-800 rounded-l py-1 px-2 self-stretch flex justify-center">
				<!-- <span class="icon-btn-sm">
					<CalendarClock />
				</span> -->
				<div class=" text-[10px] text-white">
					{new Date(entry.timestamp).toLocaleString().split(", ")[0]}
				</div>
				<div class=" text-[10px] text-white">
					{new Date(entry.timestamp).toLocaleString().split(", ")[1]}
				</div>
			</div>

			<!-- {#if error}
				<span class="icon-btn-sm text-red-600">
					<TriangleAlert />
				</span>
			{/if} -->

			<div class="py-2">
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
		<div class="fcol-1 pt-2 pl-2">
			<div class="frow-2 items-center">
				<span class="icon-btn-sm">
					<Folder />
				</span>
				{entry.cwd}
			</div>
			{#if entry.err !== ""}
				<div class="frow-2 items-center">
					<span class="icon-btn-sm text-red-600">
						<TriangleAlert />
					</span>
					{entry.err}
				</div>
			{/if}

			{#if error}
				<div class="frow-2 items-center">
					<span class="icon-btn-sm">
						<Binary />
					</span>
					{entry.code === null ? "N/A" : entry.code}
				</div>
			{/if}

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
		</div>
	{/if}
</div>
