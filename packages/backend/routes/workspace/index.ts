import { pathExist } from "../../lib/fs";

import { mkdir, } from "node:fs/promises";

import { copyApp, initiateWorkspace, runProject } from "../../lib/workspace";

import { headers, type RouteType } from "../../lib/_shared"
import { routes as dependencyRoutes } from "../workspace/dependency"
export const routes: RouteType = {
    ...dependencyRoutes,
    "/workspace/set": {
        POST: async req => {



            const { path } = await req.json() as { path: string }

            const path_exist = await pathExist(path)

            if (!path_exist) {
                await mkdir(path)
                await initiateWorkspace(path)
            }

            if (!await pathExist(path + "/app"))
                await copyApp(path)

            runProject(path)


            return Response.json({}, { headers })
        }
    }
}
