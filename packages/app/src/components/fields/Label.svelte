<script lang="ts">
	let {
		label,
		mandatory = false,
	}: {
		label: string;
		mandatory?: boolean;
	} = $props();
</script>

<div class="  min-w-16 px-1 h-full flex items-center">
	{label}
	{#if mandatory}
		<span class="text-red-500">*</span>
	{/if}
</div>
