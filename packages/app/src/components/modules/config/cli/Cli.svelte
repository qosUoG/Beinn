<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import { cnoc_controller } from "$controllers/cnoc.svelte";
	import { zeropad } from "$lib/utils";
	import { stairsArrowDownLeft } from "@lucide/lab";
	import { Clock, ListVideo, SendHorizontal } from "@lucide/svelte";
	import { tick } from "svelte";
	import type { Attachment } from "svelte/attachments";

	const month_texts = [
		"Jan",
		"Feb",
		"Mar",
		"Apr",
		"May",
		"Jun",
		"Jul",
		"Aug",
		"Sep",
		"Oct",
		"Nov",
		"Dec",
	];

	const refreshAttachment: Attachment<HTMLDivElement> = (
		element: HTMLDivElement
	) => {
		if (cnoc_controller.is_refreshing) {
			element.scrollTo({
				top: element.scrollHeight,
				left: element.scrollLeft,
				behavior: "instant",
			});
			cnoc_controller.scroll_position = element.scrollHeight;
		}
		return () => {};
	};

	let input = $state("");

	async function keyDownHandler(e: KeyboardEvent) {
		switch (e.key) {
			case "Enter":
				e.preventDefault();
				cnoc_controller.send(input);
				input = "";
				return;
			case "ArrowDown": {
				e.preventDefault();
				input = cnoc_controller.getLaterQuery();
			}
			case "ArrowUp":
				e.preventDefault();
				input = cnoc_controller.getEarlierQuery();
			default:
				cnoc_controller.updateQuery(input);
		}
	}
</script>

<div class="fcol-4 h-full">
	<div class="frow justify-between">
		<button
			class={cn(
				"icon-btn-sm  rounded border-1 border-green-500 text-slate-700",
				cnoc_controller.show_timetext
					? "bg-green-500"
					: "text-green-500"
			)}
			onclick={() => {
				cnoc_controller.show_timetext = !cnoc_controller.show_timetext;
			}}>
			<Clock />
		</button>

		<button
			class={cn(
				" border-white border-1 icon-btn-sm wrapped",
				cnoc_controller.is_refreshing ? "bg-white" : "text-white"
			)}
			onclick={() => {
				cnoc_controller.is_refreshing = !cnoc_controller.is_refreshing;
			}}><ListVideo /></button>
	</div>

	<div
		{@attach refreshAttachment}
		class="flex-grow overflow-y-scroll font-mono tracking-tighter font-light scrollbar-slate-200">
		{#each cnoc_controller.log_entries as entry}
			<div class="frow">
				{#if cnoc_controller.show_timetext}
					{@render timetext(entry.timestamp)}
				{/if}
				<div
					class="text-slate-100 text-wrap flex-grow whitespace-break-spaces break-all text-[11px]">
					{entry.message.replace(/\u001b\[.*?m/g, "")}
				</div>
			</div>
		{/each}
	</div>

	<div class="w-full frow-2">
		<input
			class="w-full bg-slate-200 wrapped"
			bind:value={input}
			onkeydown={keyDownHandler} />

		<button
			class="icon-btn-sm rounded border-slate-200 border-1 text-slate-200"
			onclick={() => {
				cnoc_controller.send(input);
				input = "";
			}}><SendHorizontal /></button>
	</div>
</div>
{#snippet timetext(timestamp: number)}
	{@const date_obj = new Date(timestamp)}
	{@const month = month_texts[date_obj.getMonth()]}
	{@const date = zeropad(date_obj.getDate())}
	{@const hour = zeropad(date_obj.getHours())}
	{@const minuet = zeropad(date_obj.getMinutes())}
	{@const second = zeropad(date_obj.getSeconds())}

	<div class="min-w-26 w-26 max-w-24 text-green-500 text-nowrap text-[11px]">
		{`${month} ${date} ${hour}:${minuet}:${second}`}
	</div>
{/snippet}
