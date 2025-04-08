


export const app_state: {
    pyproc: Deno.ChildProcess | undefined
    ws: WebSocket | undefined
    logs: {
        source: "backend" | "qoslabapp",
        content: string,
        timestamp: number
    }[]
} = {
    pyproc: undefined,
    ws: undefined,
    logs: []
}

export const postCli = (source: "backend" | "qoslabapp", content: string) => {


    if (app_state.ws === undefined)
        app_state.logs.push({ source, content, timestamp: Date.now() })
    else app_state.ws.send(JSON.stringify({ logs: [{ source, content, timestamp: Date.now() }] }))

}