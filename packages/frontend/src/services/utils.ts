export const postRequestJsonInOut = async (url: string, payload: Record<any, any>, headers: HeadersInit = {
    "Content-type": "application/json"
}) => {

    return await (await fetch(url, {
        method: "POST",
        body: JSON.stringify(payload),
        headers
    })).json()

}

export const qoslabappUrl = (path: string) => `http://localhost:8000/${path}`

export const qoslabappWs = (path: string) => `ws://localhost:8000/${path}`

export const backendUrl = (path: string) => `http://localhost:4000/${path}`

