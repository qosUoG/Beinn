import { serve } from "bun"
import { type BackendMessage } from "shared-types"
import { getDirectoryInfo } from "./handlers/set_directory";

serve({
    port: 4000,
    hostname: "localhost",
    fetch(req, server) {

        const url = new URL(req.url)

        if (url.pathname === "/backend") {
            console.log(`upgrade!`);

            const success = server.upgrade(req, {});
            return success
                ? undefined
                : new Response("WebSocket upgrade error", { status: 400 });
        }




    },
    websocket: {
        open(ws) {
            console.log("backend: Connection opened")

        },
        async message(ws, message: string) {
            const msg = JSON.parse(message) as BackendMessage
            switch (msg.command) {
                case "Set-Directory":
                    ws.send(JSON.stringify(await getDirectoryInfo(msg.payload.path)))
            }
        },
    }
})