import { project_directory, setProjectDirectory } from "$states/project_directory.svelte"
import { type BackendMessage, type ToFrontendMessage } from "shared-types"


function send<T extends BackendMessage>(message: T) {
    backend_socket.send(JSON.stringify(message))
}

export const sendSetDirectory = (path: string) => {
    send(
        {
            command: "Set-Directory",
            payload: { path }
        }
    )
}

export const backend_socket = new WebSocket("ws://localhost:4000/backend", "backend")

backend_socket.onopen = () => {
    console.log("opening connection to backend")
    sendSetDirectory("/Users/harry/Downloads")
}
backend_socket.onmessage = (e) => {

    const msg = JSON.parse(e.data) as ToFrontendMessage
    switch (msg.command) {
        case "Project-Directory-Info":
            setProjectDirectory(msg.payload)
    }
}
