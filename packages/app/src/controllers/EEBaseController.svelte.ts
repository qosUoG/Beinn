import { deepCopy, type Prettify } from "$lib/utils"
import { dependency_controller } from "./DependencyController.svelte"
import { beinn_log_controller } from "./LogController.svelte"
import type { AllParamTypes } from "./Params.svelte"
import { workspace_controller } from "./WorkspaceController.svelte"

export type Imports = { module: string, cls: string }[]

export type Instance = {
    name: string,
    module: string,
    cls: string,
    params: Record<string, AllParamTypes>,
    temp_params: Record<string, AllParamTypes>
}

export abstract class EEBaseController {

    #instances = $state<Record<string, Instance>>({})
    get instances() {
        return Object.values(this.#instances)
    }
    imports: Imports = $state([])

    temp_module: string = $state("")
    temp_cls: string = $state("")
    temp_name: string = $state("")

    composite_opens = $state<Record<string, boolean>>({})

    eetype: "equipment" | "experiment"

    constructor(eetype: "equipment" | "experiment") {
        this.eetype = eetype
        workspace_controller.registerOnOpen(() => {

        })
        workspace_controller.registerCallback(`${eetype}:imports`, (imports: Imports) => {
            this.imports = imports
        })
        workspace_controller.registerCallback(`${eetype}:create`, (instance: Prettify<Omit<Instance, "temp_params">>) => {

            this.#instances[instance.name] = { ...instance, temp_params: deepCopy(instance.params) }

            for (const [key, value] of Object.entries(instance.params))
                if (value.type === "composite" && this.composite_opens[`${instance.name}.${key}`] === undefined)
                    this.composite_opens[`${instance.name}.${key}`] = false


            if (instance.name === this.temp_name && instance.module === this.temp_module && instance.cls === this.temp_cls) {
                this.temp_name = ""
                this.temp_module = ""
                this.temp_cls = ""
            }
        })

        workspace_controller.registerCallback(`${eetype}:save`, ({ name, params }: { name: string, params: Prettify<Instance["params"]> }) => {
            this.#instances[name].params = params
        })

        workspace_controller.registerCallback(`${eetype}:remove`, (name: string) => {
            delete this.#instances[name]
        })



    }

    updateImports() {
        workspace_controller.sendCommand(`${this.eetype}:imports`, { packages: dependency_controller.hasDriverPackageNames })
    }

    create() {
        for (const instance of Object.values(this.#instances)) {
            if (instance.name === this.temp_name) {
                beinn_log_controller.append(`ERROR Instance with name ${this.temp_name} already exists`)
                return
            }
        }
        const instance: Instance = {

            name: this.temp_name,
            module: this.temp_module,
            cls: this.temp_cls,
            params: {},
            temp_params: {}
        }
        workspace_controller.sendCommand(`${this.eetype}:create`, instance)
    }

    save(name: string) {
        if (!(name in this.#instances)) {
            beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
            return
        }

        workspace_controller.sendCommand(`${this.eetype}:save`, {
            name,
            params: this.#instances[name].temp_params
        })
    }

    remove(name: string) {
        if (!(name in this.#instances)) {
            beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
            return
        }
        workspace_controller.sendCommand(`${this.eetype}:remove`, name)
    }
}

