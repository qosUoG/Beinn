
import { type ToExperimentMessage } from "shared-types"



function send<T extends ToExperimentMessage>(message: T) {
    experiment_socket.send(JSON.stringify(message))
}

export const sendStartExperiment = () => {
    send(
        {
            command: "Start-Experiment",
            payload: undefined
        }
    )
}

let experiment_socket: WebSocket

export const experiment_socket_connect = () => {
    experiment_socket = new WebSocket("ws://localhost:8765", "experiment")

    experiment_socket.onopen = () => {
        console.log("OPENED connection to experiment")
        experiment_connection.connecting = true
    }

    experiment_socket.onclose = () => {
        console.log("CLOSED connection to experiment")
        experiment_connection.connecting = false
    }

    experiment_socket.onmessage = (e) => {

    }
}



export let experiment_connection = $state({ connecting: false })


