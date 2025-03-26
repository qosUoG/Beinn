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

    if (app_state.pyproc !== undefined) {
        const res = await fetch("http://localhost:8000/workspace/forcestop")
        console.log(await res.json())
        app_state.pyproc?.kill()
        // wait for 100 ms
        await new Promise(_ => setTimeout(_, 1000));
    }

    process.exit();
});