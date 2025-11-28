<script lang="ts">
    import type { Cli } from "$controllers/cli.svelte";
    import { onMount } from "svelte";

    let { cli = $bindable() }: { cli: Cli } = $props();

    let hovering = $state(false);
    let element: HTMLDivElement | undefined = $state(undefined);

    onMount(() => {
        if (element) element.scrollTop = cli.scroll_height;
    });

    $effect(() => {
        if (element === undefined) return;

        cli.command;
        cli.logs.entries.length;

        if (cli.follow_scroll) {
            cli.scroll_height = element.scrollHeight;
            element.scrollTop = element.scrollHeight;
        }
    });
</script>

<div
    role={"cli"}
    bind:this={element}
    class="overflow-y-scroll fcol text-white min-h-0 h-full scrollbar-slate-300 w-full"
    onmouseenter={() => {
        hovering = true;
    }}
    onmouseleave={() => {
        hovering = false;
    }}
    onwheel={() => {
        cli.scroll_height = element!.scrollTop;

        if (hovering) cli.follow_scroll = false;
    }}
>
    {#each cli.logs.entries as entry}
        <div
            class="text-white text-left font-mono whitespace-pre-wrap break-all text-[11px]"
        >
            {entry}
        </div>
    {/each}
</div>
