<script lang="ts">
	import { Plus } from "@lucide/svelte";
	import InputField from "$components/fields/InputField.svelte";
	import TabSelect from "$components/fields/TabSelect.svelte";

	let cls = $state("");
	let module = $state("");
	let name = $state("");
</script>

<div class="bg-slate-100 rounded p-1 pb-2 fcol">
	<div class="title text-center wrapped relative mb-1">
		New Equipment
		<button
			class="absolute right-0 top-0 flex items-center h-full bg-blue-600 rounded aspect-square justify-center icon-btn-sm text-white"
			aria-label="Add equipment"
			onclick={async () => {}}>
			<Plus />
		</button>
	</div>

	<div
		class="fcol *:border-1 *:border-slate-400 *:border-b-0 last:border-b-1 last:border-b-slate-400">
		<InputField label="name" bind:value={name} mandatory />
		<InputField label="import" bind:value={name} mandatory />
	</div>
</div>
