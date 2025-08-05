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
    return (e) => {
        const r = {

            t: 0,
            l: 0,
            x: 0,
            y: 0,
        };

        $effect(() => {






            const cancel_mousedown = on(e, "mousedown", (m) => {
                moving = true;
                const { left, top } = target.getBoundingClientRect();
                const { left: parent_left, top: parent_top } = parent.getBoundingClientRect();
                r.t = top - parent_top
                r.l = left - parent_left;
                r.x = m.clientX;
                r.y = m.clientY;


            });

            const cancel_mousemove = on(window, "mousemove", (m) => {
                if (!moving) return;
                let top = r.t + m.clientY - r.y;
                let left = r.l + m.clientX - r.x;

                if (top < 8) top = 8
                if (left < 8) left = 8



                target.style.top = `${top}px`;
                target.style.left = `${left}px`;

                setTimeout(() => {
                    onmove({ top, left })
                })


            });

            const cancel_mouseup = on(window, "mouseup", () => {
                moving = false;
            });

            return () => {
                cancel_mousedown();
                cancel_mousemove();
                cancel_mouseup();
            }
        })
    };
}


export function resize(
    v: "top" | "bottom" | null,
    h: "left" | "right" | null,
    parent: HTMLElement,
    target: HTMLElement,
    onresize: ({ width, height, top, left }: { width: number, height: number, top: number, left: number }) => void,

)
    : Attachment<HTMLElement> {
    return (e) => {
        const r = {
            resizing: false,
            h: { w: 0, l: 0, from: null, x: 0 } as { w: number, l: number, from: "left" | "right" | null, x: number },
            v: { h: 0, t: 0, from: null, y: 0 } as { h: number, t: number, from: "top" | "bottom" | null, y: number },
        };
        $effect(() => {





            const cancel_mousedown = on(e, "mousedown", (m) => {
                r.resizing = true
                const { width, height, left, top } = target.getBoundingClientRect();
                const { left: parent_left, top: parent_top } = parent.getBoundingClientRect();

                r.h = { w: width, l: left - parent_left, from: h, x: m.clientX }
                r.v = { h: height, t: top - parent_top, from: v, y: m.clientY }
            })

            const cancel_mousemove = on(window, "mousemove", (m) => {

                if (!r.resizing) return


                let width = r.h.w
                let height = r.v.h
                let left = r.h.l
                let top = r.v.t

                if (r.h.from) {

                    const delta = m.clientX - r.h.x;
                    if (r.h.from === "right") {
                        width = r.h.w + delta;
                        if (width < 400) width = 400

                    } else {
                        left = r.h.l + delta;
                        width = r.h.w - delta;

                        if (left < 8) left = 8
                        if (width < 400) width = 400
                    }
                }
                if (r.v.from) {

                    const delta = m.clientY - r.v.y;
                    if (r.v.from === "bottom") {
                        height = r.v.h + delta;
                        if (height < 250) height = 250



                    } else {
                        top = r.v.t + delta;
                        height = r.v.h - delta;

                        if (top < 8) top = 8
                        if (height < 250) height = 250
                    }
                }



                target.style = `width: ${width}px; height: ${height}px; left: ${left}px; top: ${top}px;`

                onresize({ width, height, top, left })
            });

            const cancel_mouseup = on(window, "mouseup", () => {
                r.resizing = false
            });

            return () => {
                cancel_mousedown();
                cancel_mousemove();
                cancel_mouseup();
            }
        })
    };
}