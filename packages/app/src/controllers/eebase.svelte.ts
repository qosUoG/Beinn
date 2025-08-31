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
            workspace_controller.registerCallback(`${eetype}:create`, (instances: ConcInstance[]) => {
                for (const instance of instances) {


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
                }
            })




            workspace_controller.registerCallback(`${eetype}:update_params`, (value: { name: string, params: Prettify<Instance["params"]> }[]) => {
                for (const { name, params } of value)
                    this.instances[name].params = params
            })

            workspace_controller.registerCallback(`${eetype}:remove`, (names: string[]) => {
                for (const name of names)
                    delete this.instances[name]
            })

        })

    }

    updateImports() {
        return workspace_controller.sendCommand(`${this.eetype}:imports`, dependency_controller.has_driver_package_names)
    }

    create(temp_instances: { name: string, module: string, cls: string }[]) {
        let res: ConcInstance[] = []
        for (const { name, module, cls } of temp_instances) {
            for (const instance of Object.values(this.instances)) {
                if (instance.name === name) {
                    beinn_log_controller.append(`ERROR Instance with name ${name} already exists`)
                    continue
                }
                res.push({ name, module, cls, params: {}, })
            }
        }
        return workspace_controller.sendCommand(`${this.eetype}:create`, res)
    }

    updateParams(names: string[]) {
        let res: { name: string, params: Record<string, AllParamTypes> }[] = []
        for (const name of names) {
            if (!(name in this.instances)) {
                beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
                return
            }
            res.push({
                name,
                params: this.instances[name].temp_params
            })
        }
        return workspace_controller.sendCommand(`${this.eetype}:update_params`, res)
    }

    remove(names: string[]) {
        let res: string[] = []
        for (const name of names) {
            if (!(name in this.instances)) {
                beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
                continue
            }
            res.push(name)
        }
        return workspace_controller.sendCommand(`${this.eetype}:remove`, res)
    }

    reload(name: string) {
        const save = JSON.parse(JSON.stringify({ ...this.instances[name] }))

        const remove_update_params_callback = workspace_controller.registerCallback(`${this.eetype}:update_params`, async (instances: { name: string, params: Prettify<Instance["params"]> }[]) => {

            for (const { name } of instances) {
                if (save.name !== name) continue

                await remove_update_params_callback()
                this.assignTempParams(name, save[name].temp_params)
            }

        })

        const remove_create_callback = workspace_controller.registerCallback(`${this.eetype}:create`, async (instances: ConcInstance[]) => {
            if (!instances.map(({ name }) => name).includes(save.name)) return

            await remove_create_callback()

            if (JSON.stringify(save[save.name].params) ===
                JSON.stringify(this.instances[save.name].temp_params))
                return

            this.assignTempParams(save.name, save[save.name].params)
            await tick()
            this.updateParams(save.name)
            return


        })

        const remove_remove_callback = workspace_controller.registerCallback(`${this.eetype}:remove`, async (names: string[]) => {
            if (!names.includes(save.name)) return

            await remove_remove_callback()
            this.create([save])
        })

        if (!(name in this.instances)) {
            beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
            return
        }

        return workspace_controller.sendCommand(`${this.eetype}:remove`, { name })
    }



    getSave() {
        const res: Record<string, Instance> = {}
        for (const instance of Object.values(this.instances))
            res[instance.name] = JSON.parse(JSON.stringify({ ...instance }))

        return res
    }

    async loadSave(save: Record<string, Instance>) {
        const request_id = {
            _value: "",
            get value() {
                return this._value
            },
            set value(value: string) {
                this._value = value
            }
        }

        const remove_update_params_callback = workspace_controller.registerCallback(`${this.eetype}:update_params`, async (instances: { name: string, params: Prettify<Instance["params"]> }[], id: string) => {
            if (id !== request_id.value) return
            await remove_update_params_callback()

            for (const { name } of instances) {
                await remove_update_params_callback()
                this.assignTempParams(name, save[name].temp_params)
            }
        })

        const remove_create_callback = workspace_controller.registerCallback(`${this.eetype}:create`, async (creates: { success: boolean, instance: ConcInstance }[], id: string) => {
            if (id !== request_id.value) return

            await remove_create_callback()

            for (const { success, instance } of creates) {
                if (!success) continue

                if (JSON.stringify(save[instance.name].params) ===
                    JSON.stringify(this.instances[instance.name].temp_params))
                    return

                this.assignTempParams(instance.name, save[instance.name].params)

            }

            await tick()
            request_id.value = this.updateParams(creates.map(({ instance }) => instance.name)) ?? ""
        })

        request_id.value = this.create(Object.values(save).map(({ name, module, cls }) => ({ name, module, cls }))) ?? ""
    }

    assignTempParams(name: string, params: Prettify<Instance["params"]>) {
        const assignParam = (obj: Prettify<Exclude<Instance["params"], "composite">>, key: string, param: SimpleParamType) => {
            if (key in obj) {
                if (obj[key].type !== param.type) return

                switch (param.type) {

                    case "select.str": {
                        if (!(obj[key] as SelectStrParam).options.includes(param.value)) {
                            (obj[key] as SelectStrParam).value = (obj[key] as SelectStrParam).options[0]
                            return
                        }
                    }
                    case "select.float":
                    case "select.int": {
                        if (!(obj[key] as SelectFloatParam).options.includes(param.value as number)) {
                            (obj[key] as SelectFloatParam).value = (obj[key] as SelectFloatParam).options[0]
                            return
                        }
                    }
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

