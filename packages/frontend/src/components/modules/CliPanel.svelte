<script lang="ts">
	import { cn } from "$components/utils.svelte";
	import Clock from "$icons/Clock.svelte";
	import Send from "$icons/Send.svelte";
	import { gstore } from "$states/global.svelte";

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

	let displaying_logs = $derived.by(() => {
		return gstore.logs
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

	function handleSend() {
		// Check if cli websocket is connected
		if (gstore.log_socket === undefined) return;

		if (!input.includes(".")) {
			// Not targeting equipment, directly send command to python
			gstore.log_socket.send(
				JSON.stringify({
					type: "general",
					command: input,
				})
			);
		} else {
			// Targeting equipment, first check if the equipment name exist
			const equipment_name = input.split(".")[0];
			for (const equipment of Object.values(gstore.equipments)) {
				if (!equipment.created) return;

				if (equipment.name === equipment_name) {
					console.log(input.slice(equipment_name.length));
					// Reconstruct the command and send to python
					gstore.log_socket.send(
						JSON.stringify({
							type: "equipment",
							id: equipment.id,
							command: input.slice(equipment_name.length),
						})
					);
				}
			}
		}

		// Record the command into the log
		gstore.logs.push({
			source: "equipment",
			timestamp: Date.now(),
			content: input,
		});
	}
</script>

<div class="max-w-170 min-w-170 w-170 h-full section bg-slate-700 fcol-1">
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
					class="text-slate-100 text-wrap flex-grow whitespace-pre-line">
					>> {content.replace(/\u001b\[.*?m/g, "")}
				</div>
			</div>
		{/each}
	</div>

	<div class=" wrapped bg-slate-200 w-full frow-2 items-center">
		<label class="frow-2 flex-grow">
			>>
			<input type="text" class="flex-grow" bind:value={input} />
		</label>
		<button class="icon-btn-sm" onclick={handleSend}><Send /></button>
	</div>
</div>
