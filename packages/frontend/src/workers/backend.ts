import { compileWorkerScript } from "./utils"

export default compileWorkerScript(() => {
    const chart_socket = new WebSocket("", "chart")

    chart_socket.onopen = () => { }
    chart_socket.onmessage = (e) => {

    }
})

