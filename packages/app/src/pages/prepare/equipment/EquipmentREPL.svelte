<script lang="ts">
	import { equipment_controller } from "$controllers/equipment.svelte";
	import { ChevronDown, ChevronRight, ChevronsDown, X } from "@lucide/svelte";
	import ParamList from "$components/param/ParamList.svelte";
	import { cn } from "$components/utils.svelte";
	import { onMount, tick } from "svelte";

	let input = $state("");
	let log_container: HTMLDivElement | undefined = $state(undefined);
	let editable: HTMLDivElement | undefined = $state(undefined);
	let follow_scroll = $state(false);

	async function keyDownHandler(e: KeyboardEvent) {
		if (equipment_controller.repl === undefined) return;
		switch (e.key) {
			case "Enter":
				e.preventDefault();
				equipment_controller.repl.write(input + "\n");
				input = "";
				return;
			case "ArrowDown": {
				e.preventDefault();
				equipment_controller.repl.cli.next();
				return;
			}
			case "ArrowUp": {
				e.preventDefault();
				equipment_controller.repl.cli.prev();
				return;
			}

			case "Tab":
				e.preventDefault();
				const range = document.createRange();
				const selection = window.getSelection()!;
				const offset = selection.getRangeAt(0).startOffset;
				input = input.slice(0, offset) + "    " + input.slice(offset);

				await tick();

				range.setStart(editable!.childNodes[0], 4 + offset);
				range.collapse(true);

				selection.removeAllRanges();
				selection.addRange(range);

				return;

			case "D":
				if (e.ctrlKey) {
					equipment_controller.closeREPL();
					return;
				}

			case "Backspace":
				if (input.length === 0) {
					e.preventDefault();
					return;
				}

				if (input.length === 1) {
					e.preventDefault();
					input = "";
				}
		}
	}
	onMount(() => {
		if (log_container) log_container.scrollTop = log_container.scrollHeight;
	});
	$effect(() => {
		if (log_container === undefined) return;
		equipment_controller.repl?.log;
		input;
		if (follow_scroll) log_container.scrollTop = log_container.scrollHeight;
	});
</script>

{#if equipment_controller.repl}
	<div
		class="h-screen w-screen backdrop-blur-lg absolute top-0 left-0 z-10000 flex items-center justify-center bg-slate-600/50">
		<div class="frow-2 h-3/4">
			<div class="bg-white rounded fcol-4 p-2">
				<div class="frow justify-between">
					<button
						class="icon-btn-sm bg-red-500 text-white"
						onclick={() => {
							if (equipment_controller.repl)
								equipment_controller.closeREPL();
						}}>
						<X />
					</button>

					{#if equipment_controller.repl.online}
						<div class="bg-green-500 rounded px-2 py-1 text-white">
							ONLINE
						</div>
					{:else}
						<div class="bg-red-500 rounded px-2 py-1 text-white">
							OFFLINE
						</div>
					{/if}

					<button
						class={cn(
							"rounded border border-slate-500",
							follow_scroll ? "bg-slate-500 text-slate-50 " : ""
						)}
						onclick={() => {
							follow_scroll = !follow_scroll;
						}}>
						<div
							class={cn(
								"icon-btn-sm ",
								follow_scroll
									? "animate-pulse text-slate-50"
									: "text-slate-500"
							)}>
							<ChevronsDown />
						</div>
					</button>
				</div>
				<div
					class="p-2 fcol-2 overflow-y-scroll scrollbar-slate-400 h-full">
					{#each equipment_controller.repl.instances as instance}
						<div class="fcol-1 bg-slate-white">
							<div
								class="  font-light text-slate-950 flex items-center px-1 text-sm justify-center underline">
								{instance.name}
							</div>

							<div>
								<div
									class={cn(
										"grid grid-cols-2 border-2 border-slate-white bg-slate-300 rounded-t p-0.5",
										instance.param_opens ? "" : "rounded-b"
									)}>
									<button
										class={cn(
											"frow items-center   pr-4 rounded-tr rounded-tl h-full"
										)}
										onclick={() => {
											instance.param_opens =
												!instance.param_opens;
										}}>
										<span class="h-3">
											{#if !instance.param_opens}
												<ChevronRight
													strokeWidth="3px" />
											{:else}
												<ChevronDown
													strokeWidth="3px" />
											{/if}
										</span>
										<div class="  wrapped px-0">Params</div>
									</button>
								</div>
								<div class="bg-white">
									<ParamList
										editable={false}
										param_opens={instance.param_opens}
										bind:composite_opens={
											instance.composite_opens
										}
										bind:params={instance.params}
										saveFn={async () => {
											await equipment_controller.save();
										}} />
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>

			<div
				class="bg-slate-700 scrollbar-slate-600 rounded w-xl p-4 fcol overflow-y-scroll fcol"
				bind:this={log_container}>
				<div
					class="text-white whitespace-pre-wrap break-all grow font-mono text-[11px] max-w-full">
					{equipment_controller.repl.log}
				</div>
				<div
					class="text-white frow font-mono text-[11px] whitespace-pre-wrap break-all
					">
					<div
						class="text-white font-mono text-[11px] text-nowrap whitespace-break-spaces min-w-7">
						{`>>> `}
					</div>

					<div
						contenteditable="plaintext-only"
						bind:innerText={input}
						bind:this={editable}
						class=" text-white font-mono text-[11px] whitespace-break-spaces break-all min-h-4 grow focus:outline-none"
						spellcheck="false"
						autocapitalize="off"
						onkeydown={keyDownHandler}
						role={"input of repl"}>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}
