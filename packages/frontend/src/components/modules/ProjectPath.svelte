<script lang="ts">
	import Loader from "$icons/Loader.svelte";

	import { gstore } from "$states/global.svelte";
	import {} from "$states/workspace.svelte";

	import { tick } from "svelte";
	import { toastError } from "./ToastController.svelte";
	import type { Err } from "qoslab-shared";

	let loading = $state(false);

	async function connectHandler() {
		loading = true;
		await tick();
		// set the project directory
		try {
			await gstore.workspace.connect();
		} catch (e) {
			toastError(e as Err);
		}
		loading = false;
	}

	async function disconnectHandler() {
		loading = true;
		await tick();
		// set the project directory
		try {
			await gstore.workspace.disconnect();
		} catch (e) {
			toastError(e as Err);
		}
		loading = false;
	}

	async function saveHandler() {
		try {
			await gstore.workspace.save();
		} catch (e) {
			toastError(e as Err);
		}
	}
</script>

<label class=" frow-1 flex-grow">
	<div class="w-fit wrapped text-nowrap bg-slate-200 flex items-center">
		Project Directory
	</div>
	<input
		spellcheck="false"
		class="flex-grow wrapped bg-slate-200"
		type="text"
		bind:value={gstore.workspace.path} />

	{#if loading}
		<div class="min-w-20 slate rounded flex">
			<div class="slate icon-btn m-auto"><Loader /></div>
		</div>
	{:else if gstore.workspace.connected}
		<button class="wrapped slate min-w-20" onclick={disconnectHandler}
			>Disconnect</button>
		<button class="wrapped slate" onclick={saveHandler}>Save</button>
		<!-- <button
			class="wrapped slate text-nowrap"
			onclick={() => {
				// Save the whole configuration to another path
			}}>Save as</button> -->
	{:else}
		<button class="wrapped slate min-w-20" onclick={connectHandler}
			>Connect</button>
	{/if}
</label>
