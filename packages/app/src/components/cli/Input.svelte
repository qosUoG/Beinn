<script lang="ts">
    import type { Cli } from "$controllers/cli.svelte";
    import { tick } from "svelte";

    let {
        cli = $bindable(),
        onEnter = undefined,
    }: { cli: Cli; onEnter?: () => Promise<void> | void } = $props();

    async function keyDownHandler(e: KeyboardEvent) {
        switch (e.key) {
            case "Enter":
                if (!e.shiftKey && !e.ctrlKey) {
                    e.preventDefault();
                    if (onEnter) await onEnter();
                }
                return;
            case "ArrowDown": {
                e.preventDefault();
                cli.next();
                return;
            }
            case "ArrowUp": {
                e.preventDefault();
                cli.prev();
                return;
            }
            case "Tab": {
                e.preventDefault();
                const range = document.createRange();
                const selection = window.getSelection()!;
                const offset = selection.getRangeAt(0).startOffset;
                cli.command =
                    cli.command.slice(0, offset) +
                    "    " +
                    cli.command.slice(offset);

                await tick();

                range.setStart(editable!.childNodes[0], 4 + offset);
                range.collapse(true);

                selection.removeAllRanges();
                selection.addRange(range);

                return;
            }
        }
    }

    let editable: HTMLDivElement | undefined = $state(undefined);
</script>

<div
    contenteditable="plaintext-only"
    bind:innerText={cli.command}
    bind:this={editable}
    class=" text-white font-mono text-[11px] whitespace-break-spaces break-all min-h-4 focus:outline-none"
    spellcheck="false"
    autocapitalize="off"
    onkeydown={keyDownHandler}
    role={"input of repl"}
></div>
