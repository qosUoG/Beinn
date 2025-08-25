import { deepCopy, type Prettify } from "$lib/utils"
import { tick } from "svelte"
import { dependency_controller } from "./dependency.svelte"
import { beinn_log_controller } from "./log.svelte"
import type { AllParamTypes, InstanceEquipmentParam, SelectFloatParam, SelectIntParam, SelectStrParam, SimpleParamType } from "./params.svelte"
import { workspace_controller } from "./workspace.svelte"
import { equipment_controller } from "./equipment.svelte"

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
            workspace_controller.registerCallback(`${eetype}:imports`, (imports: Imports) => {
                this.imports = imports
            })
            workspace_controller.registerCallback(`${eetype}:create`, ({ success, instance }: { success: boolean, instance: ConcInstance }) => {
                console.log({ success, instance })
                if (!success) return

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



            workspace_controller.registerCallback(`${eetype}:update_params`, ({ name, params }: { name: string, params: Prettify<Instance["params"]> }) => {
                this.instances[name].params = params

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



    getSave() {
        const res: Record<string, Instance> = {}
        for (const instance of Object.values(this.instances))
            res[instance.name] = JSON.parse(JSON.stringify({ ...instance }))

        return res
    }

    async loadSave(save: Record<string, Instance>) {

        let save_pending_create: string[] = Object.keys(save)
        let save_pending_params: string[] = Object.keys(save)

        const save_update_params = async (instance: Instance) => {
            // Check if params need update
            if (JSON.stringify(save[instance.name].params) ===
                JSON.stringify(this.instances[instance.name].temp_params))
                return

            this.assignTempParams(instance.name, save[instance.name].params)
            await tick()
            this.updateParams(instance.name)

        }

        const remove_create_callback = workspace_controller.registerCallback(`${this.eetype}:create`, async ({ success, instance }: { success: boolean, instance: ConcInstance }) => {
            if (!save_pending_create.includes(instance.name)) return

            save_pending_create = save_pending_create.filter(name => name !== instance.name)

            if (save_pending_create.length === 0)
                await remove_create_callback(
                    async () => {
                        for (const save_instance of Object.values(save))
                            if (save_instance.name in this.instances)
                                await save_update_params(save_instance)
                    })

        })

        for (const instance of Object.values(save))
            this.create(instance.name, instance.module, instance.cls)

        await tick()

        const remove_update_params_callback = workspace_controller.registerCallback(`${this.eetype}:update_params`, async ({ name, params }: { name: string, params: Prettify<Instance["params"]> }) => {
            if (!save_pending_params.includes(name)) return
            save_pending_params = save_pending_params.filter(name => name !== name)


            this.assignTempParams(name, save[name].temp_params)
            await tick()

            if (save_pending_params.length === 0)
                await remove_update_params_callback()
        })
    }

    assignTempParams(name: string, params: Prettify<Instance["params"]>) {
        const assignParam = (obj: Prettify<Exclude<Instance["params"], "composite">>, key: string, param: SimpleParamType) => {
            if (key in obj) {
                if (obj[key].type !== param.type) return

                switch (param.type) {

                    case "select.str": if (!(obj[key] as SelectStrParam).options.includes(param.value)) return
                    case "select.float": if (!(obj[key] as SelectFloatParam).options.includes(param.value as number)) return
                    case "select.int": if (!(obj[key] as SelectIntParam).options.includes(param.value as number)) return
                    case "instance.equipment": if (!((param as InstanceEquipmentParam).name in equipment_controller.instances)) return

                }

                if (obj[key].type === "instance.equipment")
                    obj[key].name = (param as InstanceEquipmentParam).name
                else
                    obj[key].value = (param as Exclude<SimpleParamType, { type: "instance.equipment" }>).value
            }
        }


        for (const instance of Object.values(this.instances)) {
            if (instance.name !== name)
                continue

            for (const [key, value] of Object.entries(params)) {
                if (value.type === "composite")
                    for (const [key, deep_value] of Object.entries(value.children))
                        assignParam(instance.params, key, deep_value)
                else
                    assignParam(instance.params, key, value)

            }
        }
    }

    reset() {
        this.instances = {}
        this.imports = []
        this.temp_module = ""
        this.temp_cls = ""
        this.temp_name = ""
    }
}

