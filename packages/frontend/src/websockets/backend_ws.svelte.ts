
// import { type ToBackendMessage, type ToFrontendMessage } from "shared-types"
// import { gstore } from "$states/global.svelte"


// function send<T extends ToBackendMessage>(message: T) {
//     backend_socket.send(JSON.stringify(message))
// }


// export const sendStartExperiment = (cwd: string, script_name: string) => {
//     send(
//         {
//             command: "Start-Experiment",
//             payload: { cwd, script_name }
//         }
//     )
// }

// let backend_socket: WebSocket

// export const backend_socket_connect = () => {
//     backend_socket = new WebSocket("ws://localhost:8000/ws")

//     backend_socket.onopen = () => {
//         console.log("OPENED connection to backend")
//         backend_connection.connecting = true
//     }

//     backend_socket.onclose = () => {
//         console.log("CLOSED connection to backend")
//         backend_connection.connecting = false
//     }

//     backend_socket.onmessage = (e) => {

//         const msg = JSON.parse(e.data) as ToFrontendMessage
//         switch (msg.command) {
//             case "Project-Directory-Info":
//                 console.log("Project-Directory-Info")
//                 gstore.workspace.directory = JSON.parse(JSON.stringify(msg.payload))
//                 break
//         }
//     }
// }



// export let backend_connection = $state({ connecting: false })


