

export const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS, POST',
    'Access-Control-Allow-Headers': 'Content-Type',
}

export async function procIsRunning(proc: Deno.ChildProcess | undefined) {

    if (proc === undefined) return false

    return await Promise.any([
        (async () => {
            await proc.status
            return false
        })(),
        new Promise<true>((resolve) => setTimeout(() => { resolve(true) }, 1000))
    ])

}