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
    onmove: ({ top, left }: { top: number, left: number }) => void,
    onmouseup?: () => void,
    onmousedown?: () => void
): Attachment<HTMLElement> {
    return (e) => {
        const r = {
            moving: false,
            t: 0,
            l: 0,
            x: 0,
            y: 0,
        };

        $effect(() => {






            const cancel_mousedown = on(e, "mousedown", (m) => {
                m.stopPropagation()
                r.moving = true;
                const { left, top } = target.getBoundingClientRect();
                const { left: parent_left, top: parent_top } = parent.getBoundingClientRect();
                r.t = top - parent_top
                r.l = left - parent_left;
                r.x = m.clientX;
                r.y = m.clientY;

                setTimeout(() => {
                    if (onmousedown) onmousedown()
                })

            });

            const cancel_mousemove = on(window, "mousemove", (m) => {

                if (!r.moving) return;
                m.stopPropagation()
                let top = r.t + m.clientY - r.y;
                let left = r.l + m.clientX - r.x;


                target.style.top = `${top}px`;
                target.style.left = `${left}px`;

                setTimeout(() => {
                    onmove({ top, left })
                })


            });

            const cancel_mouseup = on(e, "mouseup", (m) => {
                m.stopPropagation()
                r.moving = false;
                console.log(r)
                setTimeout(() => {

                    if (onmouseup) onmouseup()
                })
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
            h: { w: 0, l: 0, r: 0, from: null, x: 0 } as { w: number, l: number, r: number, from: "left" | "right" | null, x: number },
            v: { h: 0, t: 0, b: 0, from: null, y: 0 } as { h: number, t: number, b: number, from: "top" | "bottom" | null, y: number },
        };
        $effect(() => {





            const cancel_mousedown = on(e, "mousedown", (m) => {
                r.resizing = true
                const { width, height, left, top, right, bottom } = target.getBoundingClientRect();
                const { left: parent_left, top: parent_top } = parent.getBoundingClientRect();

                r.h = { w: width, l: left - parent_left, r: right - parent_left, from: h, x: m.clientX }
                r.v = { h: height, t: top - parent_top, b: bottom - parent_top, from: v, y: m.clientY }
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
                        const new_left = r.h.l + delta;
                        const new_width = r.h.w - delta;

                        if (new_left < 8) {
                            left = 8
                            width = r.h.r - 8
                        }

                        else if (new_width < 400) {
                            left = r.h.r - 400
                            width = 400
                        } else {
                            left = new_left
                            width = new_width
                        }
                    }
                }
                if (r.v.from) {

                    const delta = m.clientY - r.v.y;
                    if (r.v.from === "bottom") {
                        height = r.v.h + delta;
                        if (height < 250) height = 250



                    } else {
                        const new_top = r.v.t + delta;
                        const new_height = r.v.h - delta;

                        if (new_top < 8) {
                            top = 8
                            height = r.v.b - 8
                        }

                        else if (new_height < 250) {
                            top = r.v.b - 250
                            height = 250
                        } else {
                            top = new_top
                            height = new_height
                        }


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