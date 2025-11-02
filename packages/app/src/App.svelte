<script lang="ts">
	import Titlebar from "$modules/titlebar/Titlebar.svelte";
	import { exit } from "@tauri-apps/plugin-process";

	import { getCurrentWindow } from "@tauri-apps/api/window";

	import { workspace_controller } from "$controllers/workspace.svelte";

	import Acquisition from "$pages/acquisition/Acquisition.svelte";
	import { app_controller } from "$controllers/app.svelte";
	import Prepare from "$pages/prepare/Prepare.svelte";

	getCurrentWindow().listen("tauri://close-requested", async () => {
		// if (await workspace_controller.kill()) await exit();
	});

	let acquisition_opened = $state(false);
</script>

<div class="w-screen h-screen fcol max-h-screen max-w-screen">
	<Titlebar />

	{#if app_controller.page === "prepare"}
		<Prepare />
	{:else if app_controller.page === "execute"}
		<Acquisition />
	{:else if app_controller.page === "analyze"}
		<!-- <div class="w-full h-full frow">
			<div class="w-full h-full frow">
				Analyze
			</div>
		</div> -->
	{/if}

	<!-- <div class="w-full grow relative">
		<div class="absolute top-0 left-0 w-full h-full frow min-h-0">
			{#if acquisition_opened}
				<Acquisition bind:open={acquisition_opened} />
			{/if}

			<Board />
		</div>

		{#if !acquisition_opened}
			<button
				class=" text-white aspect-auto frow items-center bg-slate-800 rounded-r px-2 py-1 w-fit absolute top-0 left-0 [writing-mode:vertical-lr]"
				onclick={() => {
					acquisition_opened = true;
				}}>
				Acquisition
			</button>
		{/if}
	</div> -->
</div>
