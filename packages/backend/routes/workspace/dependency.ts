import { readAllUvDependencies } from "../../lib/workspace";
import { $, file, type RouterTypes } from "bun";
import { headers, type RouteType } from "../../lib/_shared"

export const routes: RouteType = {

    "/workspace/dependency/check_init": {
        POST: async req => {
            const { path, directory } = await req.json() as { directory: string, path: string }
            console.log(path + "/" + directory + "/__init__.py")
            return Response.json({ success: await file(path + "/" + directory + "/__init__.py").exists() }, { headers })
        }
    },
    "/workspace/dependency/add": {
        POST: async req => {
            const { path, source } = await req.json() as { source: string, path: string }
            $.cwd(path)
            // Could be from pip, git path or local path
            await $`uv add ${{ raw: source }}`
            return Response.json({}, { headers })
        }
    },
    "/workspace/dependency/remove": {
        POST: async req => {
            const { path, name } = await req.json() as { name: string, path: string }
            $.cwd(path)
            await $`uv remove ${name}`
            return Response.json({}, { headers })
        }
    },
    "/workspace/dependency/read_all": {
        POST: async req => {
            const { path } = await req.json() as { path: string }
            return Response.json(await readAllUvDependencies(path), { headers })
        }
    },

    // "/workspace/dependency/read": {
    //     POST: async req => {
    //         const { path, name } = await req.json() as { path: string, name: string }
    //         return Response.json({
    //             dependency: (await readAllUvDependencies(path)).dependencies
    //                 .filter((dependency) => dependency.name = name)[0]
    //         }, { headers })
    //     }
    // },
}
