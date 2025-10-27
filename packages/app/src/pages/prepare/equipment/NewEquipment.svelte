<script lang="ts">
	import { equipment_controller } from "$controllers/equipment.svelte";

	import { Plus } from "@lucide/svelte";
	import InputField from "$components/fields/InputField.svelte";

	import Label from "$components/fields/Label.svelte";

	import { cn, getClickOutsideAttachment } from "$components/utils.svelte";
	import { experiment_controller } from "$controllers/experiment.svelte";
	import { tick } from "svelte";

	let open = $state(false);

	const clickoutside = getClickOutsideAttachment(() => {
		open = false;
	});
</script>

<div class="bg-white rounded p-1 pb-2 fcol min-h-[125px]">
	<div class="title text-center wrapped relative mb-1">
		New Equipment
		{#if experiment_controller.editable}
			<button
				class="absolute right-0 top-0 flex items-center h-full bg-blue-600 rounded aspect-square justify-center icon-btn-sm text-white"
				onclick={async () => {
					const success = await equipment_controller.create(
						equipment_controller.temp
					);

					await tick();

					if (success) {
						equipment_controller.temp = {
							name: "",
							module: "",
							cls: "",
						};
						await equipment_controller.save();
					}
				}}>
				<Plus />
			</button>
		{:else}
			<span
				class="absolute right-0 top-0 flex items-center h-full bg-slate-300 rounded aspect-square justify-center icon-btn-sm text-white">
				<Plus />
			</span>
		{/if}
	</div>

	<div
		class="fcol *:border-1 *:border-slate-400 *:border-b-0 last:border-b-1 last:border-b-slate-400">
		<InputField
			label="name"
			bind:value={equipment_controller.temp.name}
			mandatory
			placeholder="Unique, alphanumeric characters only"
			onkeydown={(e: KeyboardEvent) => {
				if (
					!/[a-zA-Z0-9_]/.test(e.key) ||
					(equipment_controller.temp.name.length === 0 &&
						/[0-9]/.test(e.key))
				)
					e.preventDefault();
			}} />

		<div class="frow items-center">
			<Label label="import" mandatory />
			<div
				{@attach clickoutside}
				class=" py-0.5 px-1 flex-grow w-fit border-l-1 border-slate-400 text-center relative">
				{#if open}
					<div
						class=" absolute bottom-0 left-0 w-full bg-slate-200 rounded border p-2">
						{#each equipment_controller.imports as { cls, module }}
							{@const selected =
								equipment_controller.temp.cls === cls &&
								equipment_controller.temp.module === module}
							<button
								class={cn(
									"text-slate-400 wrapped  w-full",
									selected
										? "bg-slate-700 text-slate-300"
										: "hover:bg-slate-300"
								)}
								onclick={() => {
									equipment_controller.temp.cls = cls;
									equipment_controller.temp.module = module;
									open = false;
								}}>
								from
								<span
									class={cn(
										" font-semibold",
										selected
											? "text-white"
											: "text-slate-950"
									)}>
									{module}
								</span>
								import
								<span
									class={cn(
										" font-semibold",
										selected
											? "text-white"
											: "text-slate-950"
									)}>
									{cls}
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
					{#if equipment_controller.temp.cls && equipment_controller.temp.module}
						from
						<span class="text-slate-950 font-semibold">
							{equipment_controller.temp.module}
						</span>
						import
						<span class="text-slate-950 font-semibold">
							{equipment_controller.temp.cls}
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
