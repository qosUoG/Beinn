import { serve } from "bun"

serve<{}>({
    fetch(request, server) {

    },
    websocket: {
        message(ws, message) {

        },
    }
})