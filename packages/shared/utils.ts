export async function timeoutLoop(timeout_ms: number, fn: () => Promise<boolean> | void) {
    const timenow = Date.now();
    while (Date.now() - timenow <= timeout_ms && await fn()) { }
}

export async function retryOnError(timeout_ms: number, fn: () => Promise<void> | void) {
    await timeoutLoop(
        timeout_ms,
        async () => {
            try {
                // Fetch experiment and equipment
                await fn();
            } catch (error) {
                return true
            }
            return false
        }
    )
}

export function capitalise(input: string) { return input[0].toUpperCase() + String(input).slice(1); }