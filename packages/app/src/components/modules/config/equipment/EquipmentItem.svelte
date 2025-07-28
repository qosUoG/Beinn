<script lang="ts">
	import DropSelect from "$components/fields/DropSelect.svelte";
	import InputField from "$components/fields/InputField.svelte";
	import TabSelect from "$components/fields/TabSelect.svelte";
	import { autofocus } from "$components/utils.svelte";
	import {
		equipment_controller,
		type Equipment,
	} from "$controllers/EquipmentController.svelte";

	import { Trash2 } from "@lucide/svelte";

	let { equipment = $bindable() }: { equipment: Equipment } = $props();
</script>

<div class="bg-slate-50 rounded p-1 flex flex-col gap-0.5">
	<div class="flex items-center w-full justify-between">
		<div class=" text-slate-950 font-medium wrapped px-0">
			{equipment.name}
		</div>
		<div class="self-stretch">
			<button
				aria-label="Remove dependency"
				class="bg-red-600 icon-btn-sm text-white"
				onclick={() => {
					equipment_controller.remove(equipment.name);
				}}>
				<Trash2 />
			</button>
		</div>
	</div>

	<div
		class="fcol *:border-1 *:border-slate-400 *:border-b-0 last:border-b-1 last:border-b-slate-400">
		{#each Object.entries(equipment.temp_params) as [label, p]}
			{#if p.type === "int" || p.type === "float" || p.type === "str"}
				<InputField
					{label}
					bind:value={p.value}
					onkeydown={(e: KeyboardEvent) => {
						if (p.type === "str") return;

						if (
							e.key === "Backspace" ||
							e.key === "Delete" ||
							e.key === "ArrowLeft" ||
							e.key === "ArrowRight"
						)
							return;
						if (/[0-9]/.test(e.key)) return;
						if (e.key === "." && p.type === "float") return;

						e.preventDefault();
					}}
					onfocus={autofocus} />
			{:else if p.type === "bool"}
				<TabSelect
					{label}
					bind:value={p.value}
					items={[
						{ key: "True", value: true },
						{ key: "False", value: false },
					]} />
			{:else if p.type === "select.float" || p.type === "select.int" || p.type === "select.str"}
				<DropSelect {label} bind:value={p.value} options={p.options} />
			{:else if p.type === "instance.equipment" || p.type === "instance.experiment"}
				<!-- TODO -->
			{:else if p.type === "composite"}
				<!-- TODO -->
			{/if}
		{/each}
	</div>
</div>
