export const cnoc_url = "ws://localhost:8001/"

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


