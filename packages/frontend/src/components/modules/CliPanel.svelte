<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Clock from "$icons/Clock.svelte";
	import Send from "$icons/Send.svelte";
	import { gstore } from "$states/global.svelte";
	import { tick } from "svelte";
	import { toastError } from "./ToastController.svelte";
	import type { Err } from "qoslab-shared";

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

	let display_time = $state(false);
	let display_backend = $state(false);
	let display_qoslabapp = $state(false);
	let display_equipment = $state(true);
	let input = $state("");
	let query = $state("");

	let query_list = $derived(
		gstore.command_history.filter((c) => c.startsWith(query) && c !== query)
	);

	// Start at the end, which is out of bound
	let query_index = $state(gstore.command_history.length);

	let displaying_logs = $derived.by(() => {
		return gstore.logs.logs
			.filter((log) => {
				if (log.source === "backend" && display_backend) return true;
				if (log.source === "qoslabapp" && display_qoslabapp)
					return true;
				if (log.source === "equipment" && display_equipment)
					return true;

				return false;
			})
			.sort((a, b) => a.timestamp - b.timestamp);
	});

	async function sendHandler() {
		try {
			gstore.workspace.sendCommand(input);
			input = "";
			query = "";

			await tick();

			query_index = query_list.length;
		} catch (e) {
			toastError(e as Err);
		}
	}

	async function keyDownHandler(e: KeyboardEvent) {
		switch (e.key) {
			case "Enter":
				e.preventDefault();
				await sendHandler();
				// handlesend shall reset everything
				return;
			case "ArrowUp": {
				e.preventDefault();
				const maybe_index = query_index - 1;
				if (maybe_index >= 0)
					// Update only if inbound
					query_index = maybe_index;
				await tick();
				if (query_index < query_list.length)
					input = query_list[query_index];
				else input = query;

				break;
			}
			case "ArrowDown":
				e.preventDefault();
				const maybe_index = query_index + 1;
				if (maybe_index <= query_list.length)
					// Update only if inbound
					query_index = maybe_index;
				await tick();
				if (query_index < query_list.length)
					input = query_list[query_index];
				else if (input === query || input === "") input = "";
				else input = query;
				break;
			default:
				// In all other cases, update query with input
				setTimeout(async () => {
					await tick();
					query = input;
					await tick();
					query_index = query_list.length;
					await tick();
				});
		}
	}
</script>

<div
	class="max-w-170 min-w-170 w-170 h-full section bg-slate-700 fcol-1 z-1000">
	<div class="frow-1">
		<button
			class={cn(
				"icon-btn-sm  rounded border-1 border-green-500 text-slate-700",
				display_time ? "bg-green-500" : "text-green-500"
			)}
			onclick={(_) => {
				display_time = !display_time;
			}}><Clock /></button>
		<button
			class={cn(
				"wrapped  border-1 border-yellow-300 ",
				display_backend
					? "bg-yellow-300 text-slate-700"
					: "text-yellow-300"
			)}
			onclick={() => {
				display_backend = !display_backend;
			}}>backend</button>
		<button
			class={cn(
				"wrapped  border-1 border-cyan-300 ",
				display_qoslabapp
					? "bg-cyan-300 text-slate-700"
					: "text-cyan-300"
			)}
			onclick={() => {
				display_qoslabapp = !display_qoslabapp;
			}}>qoslabapp</button>
		<button
			class={cn(
				"wrapped  border-1 border-indigo-300 ",
				display_equipment
					? "bg-indigo-300 text-slate-700"
					: "text-indigo-300"
			)}
			onclick={() => {
				display_equipment = !display_equipment;
			}}>equipment</button>
	</div>
	<div class="  flex-grow fcol-2 overflow-y-scroll scrollbar section">
		{#each displaying_logs as { source, content, timestamp }}
			{@const dateobj = new Date(timestamp)}
			{@const month = month_texts[dateobj.getMonth()]}
			{@const date = dateobj.getDate()}
			{@const hour = dateobj.getHours()}
			{@const minuet = dateobj.getMinutes()}
			{@const second = dateobj.getSeconds()}

			<div class="frow-1 items-start">
				{#if display_time}
					<div
						class="min-w-24 w-24 max-w-24 text-green-500 text-nowrap">
						{month}
						{date}
						{hour}:{minuet}:{second}
					</div>
				{/if}

				<div
					class={cn(
						"min-w-16 w-16 max-w-16 frow-1 text-nowrap",
						source === "backend" ? "text-yellow-300" : "",
						source === "qoslabapp" ? "text-cyan-300" : "",
						source === "equipment" ? "text-indigo-300" : ""
					)}>
					{source}
				</div>

				<div
					class="text-slate-100 text-wrap flex-grow whitespace-pre-line break-all">
					>> {content.replace(/\u001b\[.*?m/g, "")}
				</div>
			</div>
		{/each}
	</div>

	<div class=" wrapped bg-slate-200 w-full frow-2 items-center">
		<label class="frow-2 flex-grow">
			>>
			<input
				type="text"
				class="flex-grow"
				bind:value={input}
				onkeydown={keyDownHandler} />
		</label>
		<button class="icon-btn-sm" onclick={sendHandler}><Send /></button>
	</div>
</div>
