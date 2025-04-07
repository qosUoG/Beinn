import { applicationError, type Result } from "qoslab-shared"

export const postRequestJsonInOut = async (url: string, payload: Record<any, any>, headers: HeadersInit = {
    "Content-type": "application/json"
}) => {
    let res
    try {

        res = await fetch(url, {
            method: "POST",
            body: JSON.stringify(payload),
            headers
        })
        if (!res.ok) throw applicationError(`Failed to POST at ${url} with payload ${JSON.stringify(payload)}`)


    } catch (error) {
        throw applicationError(`fetch threw error at ${url} with payload ${JSON.stringify(payload)}`)
    }

    let txt
    try {
        txt = await res.text()
        const obj = JSON.parse(txt) as Result
        if (!obj.success) throw obj.err
        return obj.value
    }
    catch (error) {
        throw applicationError(`json parsing threw error at ${url} with payload ${JSON.stringify(payload)}, returning ${txt}`)
    }

}

export const getRequestJsonOut = async (url: string) => {
    let res
    try {

        res = await fetch(url, { method: "GET" })
        if (!res.ok) throw applicationError(`Failed to GET at ${url}`)

    } catch (error) {
        throw applicationError(`fetch threw error at ${url}`)
    }

    let txt
    try {
        txt = await res.text()
        const obj = JSON.parse(txt) as Result
        if (!obj.success) throw obj.err
        return obj.value
    }
    catch (error) {
        throw applicationError(`json parsing threw error at ${url}, returning ${txt}`)
    }
}

export const qoslabappUrl = (path: string) => `http://localhost:8000/${path}`

export const qoslabappWs = (path: string) => `ws://localhost:8000/${path}`

export const backendUrl = (path: string) => `http://localhost:4000/${path}`

export const backendWs = (path: string) => `ws://localhost:4000/${path}`

