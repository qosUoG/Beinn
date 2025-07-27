<script lang="ts">
	import Tick from "$icons/Tick.svelte";

	import EEPathSelect from "./EEPathSelect.svelte";
	import FixedField from "$components/reuseables/Fields/FixedField.svelte";
	import { tick } from "svelte";
	import type { EE } from "$states/ee.svelte";
	import { pushLog } from "$components/modules/LogPanelController.svelte";

	let {
		ee,
		options,
		onconfirm,
	}: {
		ee: EE;
		options: { cls: string; modules: string[] }[];
		onconfirm: () => void;
	} = $props();

	let temp_module_cls = $state(ee.module_cls);
</script>

<div class="frow-2 min-w-0">
	{#if !ee.created}
		<EEPathSelect bind:value={temp_module_cls} {options} />

		<button
			class="icon-btn-sm green"
			onclick={async () => {
				if (temp_module_cls.cls === "" || temp_module_cls.module === "")
					return;

				try {
					ee.module_cls_throwable = { ...temp_module_cls };
				} catch {
					await pushLog(
						"beinn",
						`Unreacheable Code reached when setting module_cls to ${JSON.stringify(temp_module_cls)} with editor`
					);
				}

				await tick();

				onconfirm();
			}}><Tick /></button>
	{:else}
		<FixedField
			key="Class"
			value={`from ${ee.module_cls.module} import ${ee.module_cls.cls}`} />

		<!-- <div class="frow-1">
			<button
				class="icon-btn-sm slate"
				onclick={() => {
					onconfirm();
				}}><Reload /></button>
		</div> -->
	{/if}
</div>
