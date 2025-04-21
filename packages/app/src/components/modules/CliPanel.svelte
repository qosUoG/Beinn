<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Clock from "$icons/Clock.svelte";
	import Send from "$icons/Send.svelte";
	import { tick } from "svelte";
	import { cli_panel } from "./CliPanelController.svelte";
	import { zeropad } from "$lib/utils";
	import Cli from "$icons/Cli.svelte";
	import { workspace } from "$states/workspace.svelte";
	import Refresh from "$icons/Refresh.svelte";

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

	let input = $state("");

	// Start at the end, which is out of bound

	async function sendHandler() {
		cli_panel.command_history.unshift(input);
		workspace.sendCode(input);
		input = "";
		cli_panel.updateQuery("");
	}

	async function keyDownHandler(e: KeyboardEvent) {
		switch (e.key) {
			case "Enter":
				e.preventDefault();
				await sendHandler();
				// handlesend shall reset everything
				return;
			case "ArrowDown": {
				e.preventDefault();
				const maybe_index = cli_panel.query_index - 1;
				if (maybe_index >= 0)
					// Update only if inbound
					cli_panel.query_index = maybe_index;
				await tick();
				input = cli_panel.query_list[cli_panel.query_index];

				// Reset query if input is ""
				await tick();
				if (input === "") cli_panel.query = "";
				break;
			}
			case "ArrowUp":
				e.preventDefault();
				const maybe_index = cli_panel.query_index + 1;
				if (maybe_index <= cli_panel.query_list.length)
					// Update only if inbound
					cli_panel.query_index = maybe_index;
				await tick();
				input = cli_panel.query_list[cli_panel.query_index];
				break;
			default:
				// In all other cases, update cli_panel.query with input
				setTimeout(async () => {
					await tick();
					cli_panel.updateQuery(input);
				});
		}
	}

	let isRefreshing = $state(false);
	let cli_element: HTMLDivElement | undefined = $state(undefined);

	$effect(() => {
		cli_panel.command_history;
		isRefreshing;
		if (isRefreshing && cli_element) {
			cli_element.scrollTo({
				top: cli_element.scrollHeight,
				left: cli_element.scrollLeft,
				behavior: "instant",
			});
		}
	});
</script>

{#if cli_panel.show}
	<div
		class="max-w-170 min-w-170 w-170 h-full section bg-slate-700 fcol-1 z-1000">
		<div class="frow justify-between">
			<div class="title text-white wrapped icon-btn-sm"><Cli /></div>

			<div class="frow-4">
				<button
					class={cn(
						" border-white border-1 icon-btn-sm wrapped",
						isRefreshing ? "bg-white" : "text-white"
					)}
					onclick={() => {
						isRefreshing = !isRefreshing;
					}}><Refresh /></button>
				<button
					class={cn(
						"icon-btn-sm  rounded border-1 border-green-500 text-slate-700",
						cli_panel.show_time ? "bg-green-500" : "text-green-500"
					)}
					onclick={() => {
						cli_panel.show_time = !cli_panel.show_time;
					}}><Clock /></button>
			</div>
		</div>
		<div
			class="  flex-grow fcol overflow-y-scroll scrollbar section font-mono font-stretch-extra-condensed tracking-tighter"
			bind:this={cli_element}>
			{#each cli_panel.cli_entries as { timestamp, message }}
				{@const dateobj = new Date(timestamp)}
				{@const month = month_texts[dateobj.getMonth()]}
				{@const date = zeropad(dateobj.getDate())}
				{@const hour = zeropad(dateobj.getHours())}
				{@const minuet = zeropad(dateobj.getMinutes())}
				{@const second = zeropad(dateobj.getSeconds())}

				<div class="frow-1 items-start">
					{#if cli_panel.show_time}
						<div
							class="min-w-24 w-24 max-w-24 text-green-500 text-nowrap">
							{`${month} ${date} ${hour}:${minuet}:${second}`}
						</div>
					{/if}

					<div
						class="text-slate-100 text-wrap flex-grow whitespace-break-spaces break-all">
						>>> {message.replace(/\u001b\[.*?m/g, "")}
					</div>
				</div>
			{/each}
		</div>

		<div
			class=" wrapped bg-slate-200 w-full frow-2 items-center font-mono font-stretch-extra-condensed tracking-tighter">
			<label class="frow-2 flex-grow">
				>>>
				<input
					type="text"
					class="flex-grow"
					bind:value={input}
					onkeydown={keyDownHandler} />
			</label>
			<button class="icon-btn-sm" onclick={sendHandler}><Send /></button>
		</div>
	</div>
{/if}
