export const cnoc_url = "ws://localhost:8080/"

export type Prettify<T> = {
    [K in keyof T]: T[K];
} & {};

export function deepCopy<T>(obj: T): T {
    return JSON.parse(JSON.stringify(obj))
}

export function zeropad(num: number) {
    if (num < 10) return `0${num}`;
    return `${num}`;
}

export function getRandomId(targetKeySet: string[]) {
    let res = window.crypto.randomUUID()
    while (targetKeySet.includes(res))
        res = window.crypto.randomUUID()

    return res
}

export const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

export const debounce = (callback: (...args: any[]) => void, wait: number) => {
    let timer: Timer
    return (...args: any[]) => {
        if (timer) clearTimeout(timer)

        timer = setTimeout(() => {
            callback(...args);
        }, wait);
    };
}

export const throttle = (callback: (...args: any[]) => void, delay: number) => {
    let lastTime = 0;
    return (...args: any[]) => {
        let now = Date.now();
        if (now - lastTime >= delay) {
            callback(...args);
            lastTime = now;
        }
    };
}


