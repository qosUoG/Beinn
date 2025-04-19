import { applicationError, isErr, type Result } from "$states/err"


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


    } catch (e) {

        if (isErr(e)) throw e
        throw applicationError(`fetch threw error at ${url} with payload ${JSON.stringify(payload)}, error: ${JSON.stringify(e)}`)
    }

    let txt
    try {
        txt = await res.text()

        const obj = JSON.parse(txt) as Result
        if (!obj.success) throw obj.err
        return obj.value
    }
    catch (e) {

        if (isErr(e)) throw e
        throw applicationError(`json parsing threw error at ${url} with payload ${JSON.stringify(payload)}, returning ${txt}, error: ${JSON.stringify(e)}`)
    }

}

export const getRequestJsonOut = async (url: string) => {
    let res
    try {

        res = await fetch(url, { method: "GET" })
        if (!res.ok) throw applicationError(`Failed to GET at ${url}`)

    } catch (e) {
        if (isErr(e)) throw e
        throw applicationError(`fetch threw error at ${url}, error: ${JSON.stringify(e)}`)
    }

    let txt
    try {
        txt = await res.text()
        const obj = JSON.parse(txt) as Result
        if (!obj.success) throw obj.err
        return obj.value
    }
    catch (e) {
        if (isErr(e)) throw e
        throw applicationError(`json parsing threw error at ${url}, returning ${txt}, error: ${JSON.stringify(e)}`)
    }
}


