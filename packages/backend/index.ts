import { serve } from "bun"
import { routes } from "./routes"

import { headers } from "./lib/_shared";
import { app_state } from "./lib/app_state";

serve({
    port: 4000,
    hostname: "localhost",
    routes: routes,
    async fetch(req) {

        // Handle CORS preflight requests
        if (req.method === 'OPTIONS')
            return new Response('', { headers });


        return new Response('Not Found', { headers, status: 404 });
    }
})



process.on("SIGINT", async () => {
    const res = await fetch("http://localhost:8000/workspace/cleanup")
    console.log(await res.json())
    app_state.pyproc?.kill()
    process.exit();
});