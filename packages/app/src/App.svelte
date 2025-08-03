<script lang="ts">
	import Titlebar from "$components/modules/titlebar/Titlebar.svelte";
	import { exit } from "@tauri-apps/plugin-process";

	import { getCurrentWindow } from "@tauri-apps/api/window";

	import Config from "$components/modules/config/Config.svelte";
	import { workspace_controller } from "$controllers/workspace.svelte";
	import { ChevronLeft, ChevronRight, ChevronsRight } from "@lucide/svelte";
	import Board from "$components/modules/charts/Board.svelte";

	getCurrentWindow().listen("tauri://close-requested", async () => {
		// const should_kill = await workspace.kill();
		// if (should_kill) await exit(0);
	});

	let open = $state(false);
</script>

<div class="w-screen h-screen fcol max-h-screen max-w-screen">
	<Titlebar />

	<div class="w-full flex-grow relative">
		<div class="absolute top-0 left-0 w-full h-full frow min-h-0">
			{#if open}
				<Config bind:open />
			{/if}

			<Board />
		</div>

		{#if !open}
			<button
				class=" text-white aspect-auto frow items-center pl-2 bg-slate-800 rounded-r h-6 w-fit absolute top-0 left-0"
				onclick={() => {
					open = true;
				}}>
				Configuration

				<span class="icon-btn-sm text-white">
					<ChevronsRight />
				</span>
			</button>
		{/if}
	</div>
</div>
