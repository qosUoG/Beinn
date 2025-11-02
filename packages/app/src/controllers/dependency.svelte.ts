import { shell } from "$lib/utils"
import { exists, readTextFile, writeTextFile } from "@tauri-apps/plugin-fs"
import { parse } from "smol-toml"

import { workspace_controller } from "./workspace.svelte"
import { tick } from "svelte"

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
    has_driver: boolean,
    updating: boolean,
    uninstalling: boolean
}

export type DependencySave = {
    source: DependencySource
    name: string,
    fullname: string,
    has_driver: boolean
}

class Dependencies {

    dependencies: Dependency[] = $state([])

    get has_updating_package() {
        return this.dependencies.find(d => d.updating) !== undefined
    }


    get has_driver_package_names() {
        return this.dependencies.filter(d => d.has_driver).map(d => d.name)
    }

    /* 
    Update list of dependencies
    */

    async readPyprojectToml({ path }: { path: string }) {


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
                    has_driver: false,
                    updating: false,
                    uninstalling: false,
                })

            else if ("git" in sources[parsed_dependency])
                uv_dependencies.push({
                    name: parsed_dependency,
                    fullname: dependency,
                    source: { type: "git", ...(sources[parsed_dependency] as Omit<GitSource, "type">) },
                    has_driver: false,
                    updating: false,
                    uninstalling: false,
                })
            else if ("path" in sources[parsed_dependency])
                uv_dependencies.push({
                    name: parsed_dependency,
                    fullname: dependency,
                    source: { type: "path", ...(sources[parsed_dependency] as Omit<PathSource, "type">) },
                    has_driver: false,
                    updating: false,
                    uninstalling: false,
                })
        }

        this.dependencies = uv_dependencies

    }

    async uninstall({ name, path }: { name: string, path: string }) {
        this.dependencies.find(d => d.name === name)!.uninstalling = true
        await tick()

        await shell({ fn: "uv", cmd: "remove " + name, cwd: path, description: `Uninstalling ${name}` })
        // Refresh the dependencies
        await this.readPyprojectToml({ path })
    }

    async update({ name }: { name: string }) {
        const dependency = this.dependencies.find(d => d.name === name)!
        dependency.updating = true

        await tick()

        await shell({ fn: "uv", cmd: `lock --upgrade-package ${name}`, cwd: workspace_controller.path!, description: `Updating dependency ${name}` })

        await shell({ fn: "uv", cmd: "sync", cwd: workspace_controller.path!, description: `Syncing dependency ${name}` })

        dependency.updating = false
    }

    async install({ path, source }: { path: string, source: DependencySource }) {
        switch (source.type) {
            case "git": {
                await shell({
                    fn: "uv",
                    cmd: `add git+${source.git}${source.subdirectory !== "" ? "#subdirectory=" + source.subdirectory : ""}${source.branch !== "" ? " --branch " + source.branch : ""}`,
                    cwd: path,
                    description: "Installing git dependency",
                })
                break
            }

            case "path": {
                await shell({ fn: "uv", cmd: `add ${source.path}${source.editable ? "--editable" : ""}`, cwd: path, description: "Installing local dependency" })
                break
            }
            case "pip": {
                await shell({ fn: "uv", cmd: `add ${source.package}`, cwd: path, description: `Installing pip dependency ${source.package}` })
                break
            }
        }

        // Refresh the dependencies
        await this.readPyprojectToml({ path })

    }



    async save() {
        await writeTextFile(workspace_controller.path! + "/.beinn/dependencies.json",
            JSON.stringify(this.dependencies.map(({ source, name, fullname, has_driver }) => ({
                source, name, fullname, has_driver,
            }))))
    }

    async loadSave(path: string) {
        if (!await exists(path + "/.beinn/dependencies.json")) return
        const save = JSON.parse(await readTextFile(path + "/.beinn/dependencies.json")) as DependencySave[]

        for (const s of save) {
            const dependency = this.dependencies.find(d => d.name === s.name)
            if (s.has_driver && dependency !== undefined)
                dependency.has_driver = true
        }
    }

    async toggleDriver(name: string) {
        const dependency = this.dependencies.find(d => d.name === name)
        if (dependency === undefined) return
        dependency.has_driver = !dependency.has_driver

    }

    reset() {
        this.dependencies = []
    }


}
export const dependency_controller = $state(new Dependencies())