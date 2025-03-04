import { type ClassValue, clsx } from "clsx";
import type { Action } from "svelte/action";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export function autofocus(e: FocusEvent) {
    (e.target as HTMLInputElement).select()
}

export async function retryTillSuccess(timeout_ms: number, fn: () => Promise<void> | void) {
    const timenow = Date.now();
    while (Date.now() - timenow <= 1000 * 5) {
        try {
            // Fetch experiment and equipment
            await fn();

        } catch (error) {
            continue;
        }
        return
    }
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