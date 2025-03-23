import { type ClassValue, clsx } from "clsx";
import type { Action } from "svelte/action";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export function autofocus(e: FocusEvent) {
    (e.target as HTMLInputElement).select()
}

export const clickoutside: Action<
    Element,
    string,
    {
        onoutsideclick: (e: CustomEvent) => void;
    }
> = (node, id) => {
    function handleclick(e: MouseEvent) {
        if (!node.contains(e.target as Node) && (e.target! as Element).id !== id)
            node.dispatchEvent(new CustomEvent("outsideclick"));
    }

    $effect(() => {
        window.addEventListener("click", handleclick);

        return () => {
            window.removeEventListener("click", handleclick);
        };
    });
};

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