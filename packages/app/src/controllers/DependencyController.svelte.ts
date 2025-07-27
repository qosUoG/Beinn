import { shell } from "$lib/utils"
import { readTextFile } from "@tauri-apps/plugin-fs"
import { parse } from "smol-toml"
import { beinn_log_controller } from "./LogController.svelte"

export type GitSource = {
    type: "git",
    git: string,
    subdirectory: string,
    branch: string
}

export type PipSource = {
    type: "pip",
    package: string
}

export type PathSource = {
    type: "path",
    path: string,
    editable: boolean
}

export type DependencySource = GitSource | PipSource | PathSource

export type Dependency = {
    source: DependencySource
    name: string,
    fullname: string,
}

class Dependencies {

    #dependencies: { value: Dependency[] } = $state({ value: [] })
    get dependencies() {
        return this.#dependencies.value
    }

    /* 
    Update list of dependencies
    */

    async get_dependencies({ path }: { path: string }) {
        beinn_log_controller.append("BEGIN GET DEPENDENCIES")

        const uv_dependencies: Dependency[] = []

        // First prepare the dependencies already installed in the workspace
        const parsed = parse(await readTextFile(path + "/pyproject.toml"))

        const sources = (parsed.tool as { uv: { sources: Record<string, object> } }).uv?.sources


        for (const dependency of (parsed.project as { dependencies: string[] }).dependencies) {

            const parsed_dependency = dependency.match(/[A-Za-z_]+[A-Za-z\-_0-9]+/g)![0]


            if (!(parsed_dependency in sources))
                uv_dependencies.push({
                    source: { type: "pip", package: parsed_dependency },
                    name: parsed_dependency,
                    fullname: dependency,

                })

            else if ("git" in sources[parsed_dependency])
                uv_dependencies.push({
                    name: parsed_dependency,
                    fullname: dependency,
                    source: { type: "git", ...(sources[parsed_dependency] as Omit<GitSource, "type">) },

                })
            else if ("path" in sources[parsed_dependency])
                uv_dependencies.push({
                    name: parsed_dependency,
                    fullname: dependency,
                    source: { type: "path", ...(sources[parsed_dependency] as Omit<PathSource, "type">) },
                })
        }

        this.#dependencies.value = uv_dependencies

        beinn_log_controller.append("END GET_DEPENDENCIES")
    }

    async uninstallDependency({ name, path }: { name: string, path: string }) {
        beinn_log_controller.append("BEGIN delete dependency")

        beinn_log_controller.append("Removing " + name + " from the workspace")

        const { success } = await shell({ fn: "uv", cmd: "remove " + name, cwd: path, logger: beinn_log_controller })
        if (!success) {
            beinn_log_controller.append("FAILED delete dependency")
            return
        }
        // Refresh the dependencies
        await this.get_dependencies({ path })

        beinn_log_controller.append("END delete dependency")


    }

    async installDependency({ path, source }: { path: string, source: DependencySource }) {
        beinn_log_controller.append("BEGIN install dependency")

        beinn_log_controller.append("Installing dependency of " + source.type + " type")

        let success = true

        switch (source.type) {
            case "git": {
                success = (await shell({ fn: "uv", cmd: `add git+${source.git}${source.subdirectory !== "" ? "#subdirectory=" + source.subdirectory : ""}${source.branch !== "" ? " --branch " + source.branch : ""}`, cwd: path, logger: beinn_log_controller })).success
                break
            }

            case "path": {
                success = (await shell({ fn: "uv", cmd: `add ${source.path}${source.editable ? "--editable" : ""}`, cwd: path, logger: beinn_log_controller })).success
                break
            }
            case "pip": {
                success = (await shell({ fn: "uv", cmd: `add ${source.package}`, cwd: path, logger: beinn_log_controller })).success
                break
            }
        }

        if (!success) {
            beinn_log_controller.append("FAILED install dependency")
            return
        }

        // Refresh the dependencies
        await this.get_dependencies({ path })
        beinn_log_controller.append("END install dependency")
    }


}
export let dependency_controller = $state(new Dependencies())