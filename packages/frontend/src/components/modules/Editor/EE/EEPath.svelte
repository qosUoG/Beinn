<script lang="ts">
	import Tick from "$icons/Tick.svelte";

	import EEPathSelect from "./EEPathSelect.svelte";
	import type { ModuleCls } from "qoslab-shared";
	import FixedField from "$components/reuseables/Fields/FixedField.svelte";
	import { tick } from "svelte";

	let {
		value = $bindable(),
		options,
		created,
		onconfirm,
	}: {
		value: ModuleCls;
		options: { cls: string; modules: string[] }[];
		created: boolean;
		onconfirm: () => void;
	} = $props();

	let temp_module_cls = $state(value);
</script>

<div class="row-2 min-w-0">
	{#if !created}
		<EEPathSelect bind:value={temp_module_cls} {options} />

		<button
			class="icon-btn-sm green"
			onclick={async () => {
				if (temp_module_cls.cls === "" || temp_module_cls.module === "")
					return;

				// if (
				// 	temp_module_cls.cls === value.cls &&
				// 	temp_module_cls.module === value.module
				// )
				// 	return;

				value = { ...temp_module_cls };

				await tick();

				onconfirm();
			}}><Tick /></button>
	{:else}
		<div class="row-2">
			<FixedField key="Module" value={value.module} />
			<FixedField key="Class" value={value.cls} />
		</div>
		<!-- <div class="row-1">
			<button
				class="icon-btn-sm slate"
				onclick={() => {
					onconfirm();
				}}><Reload /></button>
		</div> -->
	{/if}
</div>
