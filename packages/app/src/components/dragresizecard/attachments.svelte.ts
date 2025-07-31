import type { Attachment } from "svelte/attachments";
import { on } from "svelte/events";

export function hover(): Attachment<HTMLElement> {
    return (element) => {
        on(element, "mouseover", () => {
            element.style.zIndex = "10"
        })
        on(element, "mouseout", () => {
            element.style.zIndex = "0"
        })
    }
}

export function move(
    parent: HTMLElement,
    target: HTMLElement,
    moving: boolean,

    onmove: ({ top, left }: { top: number, left: number }) => void,
): Attachment<HTMLElement> {
    return (_) => {
        const r = {

            t: 0,
            l: 0,
            x: 0,
            y: 0,
        };

        on(window, "mousedown", (m) => {
            moving = true;
            const { left, top } = target.getBoundingClientRect();
            const { left: parent_left, top: parent_top } = parent.getBoundingClientRect();
            r.t = top - parent_top
            r.l = left - parent_left;
            r.x = m.clientX;
            r.y = m.clientY;


        });

        on(window, "mousemove", (m) => {
            if (!moving) return;
            const top = r.t + m.clientY - r.y;
            const left = r.l + m.clientX - r.x;

            target.style = `top: ${top}px; left: ${left}px;`
            onmove({ top, left })
        });

        on(window, "mouseup", () => {
            moving = false;
        });
    };
}


export function resize(
    v: "top" | "bottom" | null,
    h: "left" | "right" | null,
    target: HTMLElement,
    onresize: ({ width, height }: { width: number, height: number }) => void,

)
    : Attachment<HTMLElement> {
    return (_) => {
        const r = {
            resizing: false,
            h: null as { w: number, l: number, from: "left" | "right" } | null,
            v: null as { h: number, t: number, from: "top" | "bottom" } | null,
        };


        on(window, "mousedown", (m) => {
            r.resizing = true
            const { width, height, left, top } = target.getBoundingClientRect();


            if (h) {
                r.h = { w: width, l: left, from: "left" }
                if (h === "right") r.h.from = "right"
            }

            if (v) {
                r.v = { h: height, t: top, from: "top" }
                if (v === "bottom") r.v.from = "bottom"
            }
        })


        on(window, "mousemove", (m) => {

            if (!r.resizing) return

            let { width, height, left, top } = target.getBoundingClientRect();

            if (r.h) {
                const delta = m.clientX - r.h.w;
                if (r.h.from === "right") {
                    width = r.h.w + delta;
                    if (width < 1) width = 1

                } else {
                    left = r.h.l + delta;
                    width = r.h.w - delta;

                    if (left < 8) left = 8
                    if (width < 24) width = 24
                }
            }
            if (r.v) {
                const delta = m.clientX - r.v.h;
                if (r.v.from === "bottom") {
                    height = r.v.h + delta;
                    if (height < 1) height = 1

                } else {
                    top = r.v.t + delta;
                    height = r.v.h - delta;

                    if (top < 8) top = 8
                    if (height < 24) height = 24
                }
            }

            target.style = `width: ${width}px; height: ${height}px; left: ${left}px; top: ${top}px;`

            onresize({ width, height })
        });

        on(window, "mouseup", () => {
            r.resizing = false
        });
    };
}