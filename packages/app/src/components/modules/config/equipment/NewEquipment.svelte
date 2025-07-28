<script lang="ts">
	import { Plus } from "@lucide/svelte";
	import InputField from "$components/fields/InputField.svelte";

	import Label from "$components/fields/Label.svelte";
	import { equipment_controller } from "$controllers/EquipmentController.svelte";
	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";
	import type { Attachment } from "svelte/attachments";
	import { on } from "svelte/events";

	let open = $state(false);

	const clickoutside = getClickOutsideAttachment(() => {
		open = false;
	});
</script>

<div class="bg-slate-50 rounded p-1 pb-2 fcol">
	<div class="title text-center wrapped relative mb-1">
		New Equipment
		<button
			class="absolute right-0 top-0 flex items-center h-full bg-blue-600 rounded aspect-square justify-center icon-btn-sm text-white"
			aria-label="Add equipment"
			onclick={() => {
				equipment_controller.create();
			}}>
			<Plus />
		</button>
	</div>

	<div
		class="fcol *:border-1 *:border-slate-400 *:border-b-0 last:border-b-1 last:border-b-slate-400">
		<InputField
			label="name"
			bind:value={equipment_controller.temp_name}
			mandatory
			placeholder="Name must be unique" />
		<div class="frow items-center">
			<Label label="import" mandatory />
			<div
				{@attach clickoutside}
				class=" py-0.5 px-1 flex-grow w-fit border-l-1 border-slate-400 text-center relative">
				{#if open}
					<div
						class="bg-white absolute bottom-0 left-0 w-full rounded border">
						{#each equipment_controller.imports as { cls, module }}
							<button
								class={cn(
									"text-slate-400 wrapped  w-full",
									equipment_controller.temp_cls === cls &&
										equipment_controller.temp_module ===
											module
										? "bg-slate-700 text-slate-500"
										: "hover:bg-slate-300"
								)}
								onclick={() => {
									equipment_controller.temp_cls = cls;
									equipment_controller.temp_module = module;
									open = false;
								}}>
								from
								<span
									class={cn(
										" font-semibold",
										equipment_controller.temp_cls === cls &&
											equipment_controller.temp_module ===
												module
											? "text-white"
											: "text-slate-950"
									)}>
									{module}
								</span>
								import
								<span
									class={cn(
										" font-semibold",
										equipment_controller.temp_cls === cls &&
											equipment_controller.temp_module ===
												module
											? "text-white"
											: "text-slate-950"
									)}>
									cls
								</span>
							</button>
						{:else}
							<button
								onclick={() => {
									open = false;
								}}
								class="text-slate-400 wrapped italic select-none cursor-default">
								No available imports ...
							</button>
						{/each}
					</div>
				{/if}
				<button
					class="w-full"
					onclick={() => {
						open = true;
					}}>
					{#if equipment_controller.temp_cls && equipment_controller.temp_module}
						from
						<span class="text-slate-950 font-semibold">
							{equipment_controller.temp_module}
						</span>
						import
						<span class="text-slate-950 font-semibold">
							{equipment_controller.temp_cls}
						</span>
					{:else}
						<span class="text-slate-400 italic"
							>Select import ...</span>
					{/if}
				</button>
			</div>
		</div>
	</div>
</div>
