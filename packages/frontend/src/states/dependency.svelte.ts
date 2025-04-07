import { backendInstallDependency, backendCheckDependencyInit, backendRemoveDependency } from "$services/backend.svelte";
import { userError, type DependencySource, type DependencyT } from "qoslab-shared";
import { getRandomId } from "$lib/utils";
import { tick } from "svelte";
import { gstore } from "./global.svelte";


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
            await backendRemoveDependency({ name: this._name, path: gstore.workspace.path });

        setTimeout(() => {
            delete gstore.workspace.dependencies?.dependencies[this.id]
        })

    }



    async install() {

        if (this.source.type === "local") {
            // Check init is available
            await backendCheckDependencyInit(
                { path: gstore.workspace.path, directory: this.source.directory }
            );

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


        const res = await backendInstallDependency({ path: gstore.workspace.path, install_string });

        this._fullname = res.fullname
        this._name = res.name
        this._installed = true
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
