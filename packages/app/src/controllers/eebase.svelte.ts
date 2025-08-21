import { deepCopy, type Prettify } from "$lib/utils"
import { tick } from "svelte"
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
    get selectable_instances() {
        return Object.keys(this.instances)
    }
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

        setTimeout(() => {


            workspace_controller.registerOnOpen(() => {
                this.updateImports()
            })
            workspace_controller.registerCallback(`${eetype}:imports`, async (imports: Imports) => {
                this.imports = imports
                await tick()
                if (this.temp_save === undefined) return
                // Create instances
                for (const instance of Object.values(this.temp_save)) {
                    this.create(instance.name, instance.module, instance.cls)
                }

            })
            workspace_controller.registerCallback(`${eetype}:create`, async (instance: ConcInstance) => {
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

                await tick()
                if (!this.save_pending_create.includes(instance.name)) return

                this.save_pending_create = this.save_pending_create.filter(name => name !== instance.name)

                // Check if params need update
                if (this.temp_save !== undefined &&
                    JSON.stringify(this.temp_save[instance.name].params) !==
                    JSON.stringify(this.instances[instance.name].temp_params)) {


                    this.instances[instance.name].temp_params = this.temp_save[instance.name].params
                    await tick()
                    this.updateParams(instance.name)

                }
            })



            workspace_controller.registerCallback(`${eetype}:update_params`, async ({ name, params }: { name: string, params: Prettify<Instance["params"]> }) => {
                this.instances[name].params = params

                await tick()
                if (!this.save_pending_params.includes(name)) return
                this.save_pending_params = this.save_pending_params.filter(name => name !== name)

            })

            workspace_controller.registerCallback(`${eetype}:remove`, (name: string) => {
                delete this.instances[name]
            })

        })

    }

    updateImports() {
        workspace_controller.sendCommand(`${this.eetype}:imports`, { packages: dependency_controller.has_driver_package_names })
    }

    create(temp_name: string, temp_module: string, temp_cls: string) {
        for (const instance of Object.values(this.instances)) {
            if (instance.name === temp_name) {
                beinn_log_controller.append(`ERROR Instance with name ${temp_name} already exists`)
                return
            }
        }
        const instance: ConcInstance = {

            name: temp_name,
            module: temp_module,
            cls: temp_cls,
            params: {},

        }
        workspace_controller.sendCommand(`${this.eetype}:create`, instance)
    }

    updateParams(name: string) {
        if (!(name in this.instances)) {
            beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
            return
        }

        workspace_controller.sendCommand(`${this.eetype}:update_params`, {
            name,
            params: this.instances[name].temp_params
        })
    }

    remove(name: string) {
        if (!(name in this.instances)) {
            beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
            return
        }
        workspace_controller.sendCommand(`${this.eetype}:remove`, { name })
    }

    temp_save: Record<string, ConcInstance> | undefined = $state(undefined)
    save_pending_create: string[] = $state([])
    save_pending_params: string[] = $state([])

    getSave() {
        const res: Record<string, ConcInstance> = {}
        for (const instance of Object.values(this.instances)) {
            res[instance.name] = {
                name: instance.name,
                module: instance.module,
                cls: instance.cls,
                params: instance.params
            }
        }
        return res
    }

    loadSave(save: Record<string, ConcInstance>) {
        this.temp_save = save
        this.save_pending_create = Object.keys(save)
        this.save_pending_params = Object.keys(save)
    }

    reset() {
        this.instances = {}
        this.imports = []
        this.temp_module = ""
        this.temp_cls = ""
        this.temp_name = ""
    }
}

