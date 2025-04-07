import { backendInstallDependency, backendCheckDependencyInit, backendRemoveDependency } from "$services/backend.svelte";
import { userError, type DependencySource, type DependencyT } from "qoslab-shared";
import { getRandomId } from "$lib/utils";
import { tick } from "svelte";
import { gstore } from "./global.svelte";


class Dependency {

    id: string = $state("")

    source: DependencySource = $state({ type: "pip", package: "" })

    name: string = $state("")

    fullname: string = $state("")

    install_string: string = $state("")
    installed: boolean = $state(false)


    shall_delete: boolean = $state(false)


    constructor(id: string, template?: DependencyT) {
        this.id = id


        // The template shall be sure is trueful of _installed or not before constructing
        if (!template) return

        this.source = template.source
        this.installed = template.installed

        if (!template.installed) return

        this.name = template.name
        this.fullname = template.fullname
    }

    toSave: () => DependencyT = () => {
        return {
            installed: this.installed,
            source: this.source,

            install_string: this.install_string,
            name: this.name,
            fullname: this.fullname
        }
    }

    uninstall = async () => {
        // Only circumstances communicating with backend
        if (this.installed && this.source.type !== "local")
            await backendRemoveDependency({ name: this.name, path: gstore.workspace.path });

        this.shall_delete = true
    }



    install = async () => {

        if (this.source.type === "local") {
            // Check init is available
            await backendCheckDependencyInit(
                { path: gstore.workspace.path, directory: this.source.directory }
            );

            this.installed = true
            this.name = this.fullname = this.install_string = this.source.directory

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

        this.fullname = res.fullname
        this.name = res.name
        this.installed = true
    }

}

export class Dependencies {

    dependencies: Record<string, Dependency> = $state({})



    constructor(dependencies?: DependencyT[]) {

        const ids: string[] = []

        if (dependencies)
            dependencies.forEach((d) => {
                // Check if exist in save
                const id = getRandomId(ids);
                ids.push(id)
                this.dependencies[id] = new Dependency(id, d)
            });
    }

    get prefixes() {
        return Object.values(this.dependencies).filter(d => d.installed).map(d => d.name)
    }

    toSave: () => DependencyT[] = () => {
        return Object.values(this.dependencies).map(d => d.toSave())
    }

    instantiate = async () => {
        const id = getRandomId(Object.keys(this.dependencies))
        const new_dependency = new Dependency(id,)
        this.dependencies[id] = new_dependency

        await tick()

        $effect(() => {
            const shall_delete = new_dependency.shall_delete
            if (shall_delete)
                delete this.dependencies[id]
        })

        return this.dependencies[id]

    }

    instantiateTemplate = (template: DependencyT) => {
        const id = getRandomId(Object.keys(this.dependencies))
        const new_dependency = new Dependency(id, template)
        this.dependencies[id] = new_dependency

        $effect(() => {
            const shall_delete = new_dependency.shall_delete
            if (shall_delete)
                delete this.dependencies[id]
        })
    }

    reset = () => {
        for (const prop of Object.getOwnPropertyNames(this.dependencies))
            delete this.dependencies[prop];
    }


}
