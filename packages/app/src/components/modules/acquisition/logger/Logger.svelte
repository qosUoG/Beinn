<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import { beinn_log_controller } from "$controllers/log.svelte";
	import { zeropad } from "$lib/utils";
	import { BrushCleaning, Clock, ListVideo } from "@lucide/svelte";
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
		if (beinn_log_controller.is_refreshing) {
			element.scrollTo({
				top: element.scrollHeight,
				left: element.scrollLeft,
				behavior: "instant",
			});
			beinn_log_controller.scroll_position = element.scrollHeight;
		}
		return () => {};
	};
</script>

<div class="fcol-4 min-h-0">
	<div class="frow justify-between">
		<button
			class={cn(
				"icon-btn-sm  rounded border-1 border-green-500 text-slate-700",
				beinn_log_controller.show_timetext
					? "bg-green-500"
					: "text-green-500"
			)}
			onclick={() => {
				beinn_log_controller.show_timetext =
					!beinn_log_controller.show_timetext;
			}}>
			<Clock />
		</button>

		<button
			class="border-red-500 border-1 text-red-500 icon-btn-sm rounded"
			onclick={beinn_log_controller.reset}><BrushCleaning /></button>

		<button
			class={cn(
				" border-white border-1 icon-btn-sm wrapped",
				beinn_log_controller.is_refreshing ? "bg-white" : "text-white"
			)}
			onclick={() => {
				beinn_log_controller.is_refreshing =
					!beinn_log_controller.is_refreshing;
			}}><ListVideo /></button>
	</div>
	<div
		{@attach refreshAttachment}
		class="flex-grow min-h-0 overflow-y-scroll font-mono tracking-tighter font-light scrollbar-slate-200">
		{#each beinn_log_controller.log_entries as entry}
			<div class="frow">
				{#if beinn_log_controller.show_timetext}
					{@render timetext(entry.timestamp)}
				{/if}
				<div
					class="text-slate-100 text-wrap flex-grow whitespace-break-spaces break-all text-[11px]">
					{entry.message.replace(/\u001b\[.*?m/g, "")}
				</div>
			</div>
		{/each}
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
