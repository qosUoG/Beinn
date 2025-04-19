

import { getRandomId, readAllUvDependencies } from "$lib/utils";

import { gstore } from "./global.svelte";
import { applicationError, userError } from "./err";
import { parse } from "smol-toml";
import { exists, readTextFile } from "@tauri-apps/plugin-fs";
import { shell } from "./utils.svelte";

export type ModuleCls = {
    module: string,
    cls: string
}

// Only types that cross boundary of backend and frontend would be here
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
        // Only circumstances communicating with backend
        if (this._installed && this.source.type !== "local")
            await shell({ fn: "uv", cmd: "remove " + this._name, cwd: gstore.workspace.path })


        setTimeout(() => {
            delete gstore.workspace.dependencies?.dependencies[this.id]
        })

    }



    async install() {

        if (this.source.type === "local") {
            // Check init is available
            if (!await exists(
                gstore.workspace.path + "/" + this.source.directory + "/__init__.py"
            )) throw userError(`Cannot add local dependency ${gstore.workspace.path + "/" + this.source.directory} as __init__.py cannot be found`)

            this._installed = true
            this._name = this._fullname = this.install_string = this.source.directory

            return
        }

        let install_string
        switch (this.source.type) {
            case "git":
                if (this.source.git === "") throw userError("git url shall not be empty")

                install_string = this.source.git;

                if (this.source.branch) install_string += `@${this.source.branch}`;
                if (this.source.subdirectory)
                    install_string += `#${this.source.subdirectory}`;

                break;

            case "path":
                if (this.source.path === "") throw userError("path shall not be empty")
                install_string = this.source.path;
                if (this.source.editable) install_string += " --editable";
                break;
            case "pip":
                if (this.source.package === "") throw userError("package shall not be empty")
                install_string = this.source.package;
                break;
        }



        await shell({ fn: "uv", cmd: "add " + install_string, cwd: gstore.workspace.path })

        // Read All dependencies and figure out which is the new one
        const current_dependency_names = Object.values(
            gstore.workspace.dependencies!.dependencies
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
