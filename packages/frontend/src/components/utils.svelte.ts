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
    HTMLDivElement,
    undefined,
    {
        onoutsideclick: (e: CustomEvent) => void;
    }
> = (node) => {
    function handleclick(e: MouseEvent) {
        if (!node.contains(e.target as Node)) {

            node.dispatchEvent(new CustomEvent("outsideclick"));
        }
    }

    $effect(() => {
        window.addEventListener("click", handleclick);

        return () => {
            window.removeEventListener("click", handleclick);
        };
    });
};