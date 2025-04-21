

import { beginProcedure, getRandomId, readAllUvDependencies, shell } from "$lib/utils";
import { exists } from "@tauri-apps/plugin-fs";
import { workspace } from "./workspace.svelte";
import { tick } from "svelte";


export type ModuleCls = {
    module: string,
    cls: string
}

export type DependencySource = {
    type: "git",

    git: string,
    subdirectory: string,
    branch: string
} | {
    type: "path",

    path: string,
    editable: boolean
} | {
    type: "pip",

    package: string
} | {
    type: "local",

    directory: string
}

export function sourceEqual(a: DependencySource, b: DependencySource) {
    if (a.type !== b.type) return false

    switch (a.type) {
        case "local":
            return a.directory === (b as Extract<DependencySource, { type: "local" }>).directory
        case "git":
            return a.git === (b as Extract<DependencySource, { type: "git" }>).git
        case "path":
            return a.path === (b as Extract<DependencySource, { type: "path" }>).path
        case "pip":
            return a.package === (b as Extract<DependencySource, { type: "pip" }>).package
    }
}

export type DependencyT_YetInstalled = {
    installed: false
    source: DependencySource
}

export type DependencyT_Installed = {
    installed: true
    source: DependencySource


    name: string,
    fullname: string,
}

export type DependencyT = DependencyT_YetInstalled | DependencyT_Installed
class Dependency {

    readonly id: string = $state("")

    source: DependencySource = $state({ type: "pip", package: "" })

    private _name: string = $state("")
    get name() {
        return this._name
    }
    private _fullname: string = $state("")
    get fullname() {
        return this._fullname
    }

    private install_string: string = $state("")
    private _installed: boolean = $state(false)
    get installed() {
        return this._installed
    }





    constructor(id: string, template?: DependencyT) {
        this.id = id


        // The template shall be sure is trueful of _installed or not before constructing
        if (!template) return

        this.source = template.source
        this._installed = template.installed

        if (!template.installed) return

        this._name = template.name
        this._fullname = template.fullname
    }

    toSave() {
        return {
            installed: this._installed,
            source: this.source,

            install_string: this.install_string,
            name: this._name,
            fullname: this._fullname
        }
    }

    async uninstall() {
        const { step, completed, unhandled } = await beginProcedure("REMOVE DEPENDENCY")

        try {
            await step("Execute command in shell",
                async () => {
                    // Only circumstances communicating with backend
                    if (this._installed && this.source.type !== "local")
                        await shell({ fn: "uv", cmd: "remove " + this._name, cwd: workspace.path })


                    setTimeout(() => {
                        delete workspace.dependencies?.dependencies[this.id]
                    })
                })

            await completed()
        }
        catch (e) {
            await unhandled(e)
        }

    }

    async install() {

        const { step, completed, failed, unhandled } = await beginProcedure("INSTALL DEPENDENCY")

        try {



            if (this.source.type === "local") {
                await step("Add local directory to dependency list",
                    async () => {
                        if (this.source.type !== "local") {
                            await failed("unreacheable code")
                            return
                        }

                        // Check init is available
                        if (!await exists(
                            workspace.path + "/" + this.source.directory + "/__init__.py"
                        )) {
                            await failed(`__init__.py cannot be found at ${workspace.path + "/" + this.source.directory}`)
                            return
                        }


                        this._installed = true
                        this._name = "local:" + this.source.directory
                        this._fullname = "local:" + this.source.directory
                        this.install_string = this.source.directory

                        await workspace.refreshAvailables_throwable()

                        await completed()

                    })

                return
            }

            const install_string = await step("Resolve dependency installation command",
                async () => {
                    let install_string
                    switch (this.source.type) {
                        case "git":
                            if (this.source.git === "") await failed("git url shall not be empty")

                            install_string = this.source.git;

                            if (this.source.branch) install_string += `@${this.source.branch}`;
                            if (this.source.subdirectory)
                                install_string += `#${this.source.subdirectory}`;

                            break;

                        case "path":
                            if (this.source.path === "") await failed("path shall not be empty")
                            install_string = this.source.path;
                            if (this.source.editable) install_string += " --editable";
                            break;
                        case "pip":
                            if (this.source.package === "") await failed("package shall not be empty")
                            install_string = this.source.package;
                            break;
                    }
                    return install_string
                })

            if (!install_string) return


            await step("Install Dependency",
                async () => {
                    await shell({ fn: "uv", cmd: "add " + install_string, cwd: workspace.path })
                })

            // Read All dependencies and figure out which is the new one
            await step("Update Dependency List",
                async () => {

                    const current_dependency_names = Object.values(
                        workspace.dependencies!.dependencies
                    )
                        .filter((d) => d.installed)
                        .map((d) => d.name);

                    for (const d of await readAllUvDependencies()) {
                        if (!current_dependency_names.includes(d.name)) {
                            this._fullname = d.fullname
                            this._name = d.name
                            this._installed = true
                            break
                        }
                    }
                })

            await tick()
            await workspace.refreshAvailables_throwable()

            await completed()
        }
        catch (e) {
            await unhandled(e)
        }
    }


}

export class Dependencies {

    readonly dependencies: Record<string, Dependency> = $state({})



    constructor(dependencies?: DependencyT[]) {

        const ids: string[] = []

        if (dependencies) {

            dependencies.forEach((d) => {
                // Check if exist in save
                const id = getRandomId(ids);
                ids.push(id)
                this.dependencies[id] = new Dependency(id, d)
            });
        }
    }

    get prefixes() {
        return Object.values(this.dependencies).filter(d => d.installed).map(d => d.name)
    }

    toSave() {
        return Object.values(this.dependencies).map(d => d.toSave())
    }



    instantiate() {
        const id = getRandomId(Object.keys(this.dependencies))
        const new_dependency = new Dependency(id,)
        this.dependencies[id] = new_dependency
        return new_dependency

    }

    instantiateTemplate(template: DependencyT) {
        const id = getRandomId(Object.keys(this.dependencies))
        const new_dependency = new Dependency(id, template)
        this.dependencies[id] = new_dependency
        return new_dependency
    }

    reset() {
        for (const prop of Object.getOwnPropertyNames(this.dependencies))
            delete this.dependencies[prop];
    }


}
