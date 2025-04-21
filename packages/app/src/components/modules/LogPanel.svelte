<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Clock from "$icons/Clock.svelte";
	import Logs from "$icons/Logs.svelte";
	import Refresh from "$icons/Refresh.svelte";
	import { zeropad } from "$lib/utils";

	import { log_panel } from "./LogPanelController.svelte";

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

	let isRefreshing = $state(false);
	let log_element: HTMLDivElement | undefined = $state(undefined);

	$effect(() => {
		log_panel.displayingLogs;
		isRefreshing;
		if (isRefreshing && log_element) {
			log_element.scrollTo({
				top: log_element.scrollHeight,
				left: log_element.scrollLeft,
				behavior: "instant",
			});
		}
	});
</script>

{#if log_panel.show}
	<div
		class="max-w-170 min-w-170 w-170 h-full section bg-slate-700 fcol-1 z-1000 relative">
		<div class="frow justify-between">
			<div class="title text-white wrapped icon-btn-sm"><Logs /></div>

			<div class="frow-4">
				<button
					class={cn(
						" border-white border-1 icon-btn-sm wrapped",
						isRefreshing ? "bg-white" : "text-white"
					)}
					onclick={() => {
						isRefreshing = !isRefreshing;
					}}><Refresh /></button>
				<div class="frow-1">
					<button
						class={cn(
							"icon-btn-sm  rounded border-1 border-green-500 text-slate-700",
							log_panel.show_time
								? "bg-green-500"
								: "text-green-500"
						)}
						onclick={() => {
							log_panel.show_time = !log_panel.show_time;
						}}><Clock /></button>
					<button
						class={cn(
							"wrapped  border-1 border-yellow-300 ",
							log_panel.show_beinn
								? "bg-yellow-300 text-slate-700"
								: "text-yellow-300"
						)}
						onclick={() => {
							log_panel.show_beinn = !log_panel.show_beinn;
						}}>beinn</button>
					<button
						class={cn(
							"wrapped  border-1 border-cyan-300 ",
							log_panel.show_meall
								? "bg-cyan-300 text-slate-700"
								: "text-cyan-300"
						)}
						onclick={() => {
							log_panel.show_meall = !log_panel.show_meall;
						}}>python</button>
				</div>
			</div>
		</div>
		<div
			class="  flex-grow fcol overflow-y-scroll scrollbar section font-mono font-stretch-extra-condensed tracking-tighter"
			bind:this={log_element}>
			{#each log_panel.displayingLogs as { type, timestamp, message }}
				{@const dateobj = new Date(timestamp)}
				{@const month = month_texts[dateobj.getMonth()]}
				{@const date = zeropad(dateobj.getDate())}
				{@const hour = zeropad(dateobj.getHours())}
				{@const minuet = zeropad(dateobj.getMinutes())}
				{@const second = zeropad(dateobj.getSeconds())}

				<div class="frow-1 items-start">
					{#if log_panel.show_time}
						<div
							class="min-w-26 w-26 max-w-24 text-green-500 text-nowrap">
							{`${month} ${date} ${hour}:${minuet}:${second}`}
						</div>
					{/if}

					<div
						class={cn(
							"min-w-16 w-16 max-w-16 frow-1 text-nowrap",
							type === "beinn" ? "text-yellow-300" : "",
							type === "meall" ? "text-cyan-300" : ""
						)}>
						{type}
					</div>

					<div
						class="text-slate-100 text-wrap flex-grow whitespace-break-spaces break-all">
						>>> {message.replace(/\u001b\[.*?m/g, "")}
					</div>
				</div>
			{/each}
		</div>
	</div>
{/if}
