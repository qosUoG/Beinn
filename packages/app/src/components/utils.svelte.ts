import { type ClassValue, clsx } from "clsx";
import type { Action } from "svelte/action";
import { on } from "svelte/events";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export function autofocus(e: FocusEvent) {
    (e.target as HTMLInputElement).select()
}

export const getClickOutsideAttachment = (closeFn: () => void) => {
    return (
        element: HTMLDivElement
    ) => {
        const destroy = on(window, "click", (event) => {
            if (
                !element.contains(event.target as Node) &&
                !event.defaultPrevented
            )
                closeFn()
        });
        return destroy;
    };
}

export const watchresize: Action<HTMLDivElement, undefined, {
    ondivresize: (e: CustomEvent<{ width: number, height: number }>) => void
}> = (node) => {
    const observer = new ResizeObserver(entries => {
        const entry = entries.at(0)

        node.dispatchEvent(
            new CustomEvent<{ width: number, height: number }>(
                "divresize", { detail: { width: entry?.target.clientWidth ?? 0, height: entry?.target.clientHeight ?? 0 } }))
    })

    $effect(() => {
        observer.observe(node)

        return () => {
            observer.unobserve(node)
        }
    })
}