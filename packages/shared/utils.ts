export async function timeoutLoop(timeout_ms: number, fn: () => Promise<boolean> | void) {
    const timenow = Date.now();
    while (Date.now() - timenow <= timeout_ms && await fn()) { }
}

export async function retryOnError(timeout_ms: number, fn: () => Promise<void> | void) {
    timeoutLoop(
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