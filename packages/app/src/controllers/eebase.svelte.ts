import { deepCopy, type Prettify } from "$lib/utils"
import { dependency_controller } from "./dependency.svelte"
import { beinn_log_controller } from "./log.svelte"
import type { AllParamTypes } from "./params.svelte"
import { workspace_controller } from "./workspace.svelte"

export type Imports = { module: string, cls: string }[]



type ConcInstance = {
    name: string,
    module: string,
    cls: string,
    params: Record<string, AllParamTypes>,
}

export type Instance = Prettify<ConcInstance & {
    temp_params: Record<string, AllParamTypes>
    param_opens: boolean
    composite_opens: Record<string, boolean>
}>

export abstract class EEBaseController<T extends Instance = Instance> {

    instances = $state<Record<string, T>>({})
    get instances_arr() {
        return Object.values(this.instances)
    }

    imports: Imports = $state([])

    temp_module: string = $state("")
    temp_cls: string = $state("")
    temp_name: string = $state("")

    eetype: "equipment" | "experiment"

    constructor(eetype: "equipment" | "experiment", createFn: (_: Instance) => T) {
        this.eetype = eetype
        workspace_controller.registerOnOpen(() => {

        })
        workspace_controller.registerCallback(`${eetype}:imports`, (imports: Imports) => {
            this.imports = imports
        })
        workspace_controller.registerCallback(`${eetype}:create`, (instance: ConcInstance) => {
            const temp_instance: Instance = {
                ...instance, temp_params: deepCopy(instance.params), param_opens: true, composite_opens: {},
            }

            for (const [key, value] of Object.entries(instance.params))
                if (value.type === "composite" && temp_instance.composite_opens[key] === undefined)
                    temp_instance.composite_opens[key] = false

            this.instances[instance.name] = createFn(temp_instance)


            if (instance.name === this.temp_name && instance.module === this.temp_module && instance.cls === this.temp_cls) {
                this.temp_name = ""
                this.temp_module = ""
                this.temp_cls = ""
            }
        })

        workspace_controller.registerCallback(`${eetype}:param`, ({ name, params }: { name: string, params: Prettify<Instance["params"]> }) => {
            this.instances[name].params = params
        })

        workspace_controller.registerCallback(`${eetype}:remove`, (name: string) => {
            delete this.instances[name]
        })



    }

    updateImports() {
        workspace_controller.sendCommand(`${this.eetype}:imports`, { packages: dependency_controller.hasDriverPackageNames })
    }

    create() {
        for (const instance of Object.values(this.instances)) {
            if (instance.name === this.temp_name) {
                beinn_log_controller.append(`ERROR Instance with name ${this.temp_name} already exists`)
                return
            }
        }
        const instance: ConcInstance = {

            name: this.temp_name,
            module: this.temp_module,
            cls: this.temp_cls,
            params: {},

        }
        workspace_controller.sendCommand(`${this.eetype}:create`, instance)
    }

    param(name: string) {
        if (!(name in this.instances)) {
            beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
            return
        }

        workspace_controller.sendCommand(`${this.eetype}:param`, {
            name,
            params: this.instances[name].temp_params
        })
    }

    remove(name: string) {
        if (!(name in this.instances)) {
            beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
            return
        }
        workspace_controller.sendCommand(`${this.eetype}:remove`, name)
    }
}

