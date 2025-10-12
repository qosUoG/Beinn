import { deepCopy, type Prettify } from "$lib/utils"
import { tick } from "svelte"
import { dependency_controller } from "./dependency.svelte"
import { beinn_log_controller } from "./log.svelte"
import type { AllParamTypes, InstanceEquipmentParam, SelectFloatParam, SelectIntParam, SelectStrParam, SimpleParamType } from "./params.svelte"
import { workspace_controller } from "./workspace.svelte"

import { shell } from "$lib/svelte_utils"
import { Command } from "@tauri-apps/plugin-shell"

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

export class EquipmentController {

    #equipments = $state<Record<string, Instance>>({})
    get equipment_names() {
        return Object.keys(this.#equipments)
    }
    get equipment_instances() {
        return Object.values(this.#equipments)
    }

    imports: Imports = $state([])

    temp_module: string = $state("")
    temp_cls: string = $state("")
    temp_name: string = $state("")




    constructor() {


        // setTimeout(() => {


        //     workspace_controller.registerOnOpen(() => {
        //         this.updateImports()
        //     })
        //     workspace_controller.registerCallback(`${eetype}:imports`, (imports: Imports) => {
        //         this.imports = imports
        //     })
        //     workspace_controller.registerCallback(`${eetype}:create`, (instances: ConcInstance[]) => {
        //         for (const instance of instances) {


        //             const temp_instance: Instance = {
        //                 ...instance, temp_params: deepCopy(instance.params), param_opens: true, composite_opens: {},
        //             }

        //             for (const [key, value] of Object.entries(instance.params))
        //                 if (value.type === "composite" && temp_instance.composite_opens[key] === undefined)
        //                     temp_instance.composite_opens[key] = false

        //             this.#equipments[instance.name] = createFn(temp_instance)


        //             if (instance.name === this.temp_name && instance.module === this.temp_module && instance.cls === this.temp_cls) {
        //                 this.temp_name = ""
        //                 this.temp_module = ""
        //                 this.temp_cls = ""
        //             }
        //         }
        //     })




        //     workspace_controller.registerCallback(`${eetype}:update_params`, (value: { name: string, params: Prettify<Instance["params"]> }[]) => {
        //         for (const { name, params } of value)
        //             this.#equipments[name].params = params
        //     })

        //     workspace_controller.registerCallback(`${eetype}:remove`, (names: string[]) => {
        //         for (const name of names)
        //             delete this.#equipments[name]
        //     })

        // })

    }

    async updateImports() {

        const res = await Command.create(
            "uv",
            ["run", "imports", "equipment", ...dependency_controller.has_driver_package_names]
            , {
                encoding: "utf8",
                cwd: workspace_controller.path!
            }).execute()

        if (res.code !== 0) {
            beinn_log_controller.append(`error while updating imports for equipment: ${res.stderr}`)
            return
        }

        this.imports = JSON.parse(res.stdout.replaceAll(/'/g, '"')) as Imports

    }

    async create() {



        // Check if equipment with same name already exists
        if (this.temp_name in this.#equipments) {
            beinn_log_controller.append(`ERROR Instance with name ${this.temp_name} already exists`)
            return
        }

        // Get the default params list of the equipment
        const res = await Command.create(
            "uv",
            ["run", "params", this.temp_module, this.temp_cls]
            , {
                encoding: "utf8",
                cwd: workspace_controller.path!
            }).execute()

        if (res.code !== 0) {
            beinn_log_controller.append(`error while creating equipment ${this.temp_name} with module ${this.temp_module} and class ${this.temp_cls}: ${res.stderr}`)
            return
        }

        console.log(res.stdout)

        // this.imports = JSON.parse(res.stdout.replaceAll(/'/g, '"')) as Imports





        // for (const { name, module, cls } of this.equipment_instances) {
        //     let found = false
        //     for (const instance of this.equipment_instances) {
        //         if (instance.name !== name) continue

        //         beinn_log_controller.append(`ERROR Instance with name ${name} already exists`)
        //         found = true
        //         break
        //     }
        //     if (found) continue
        //     res.push(
        //         {

        //             name: name,
        //             module: module,
        //             cls: cls,
        //             params: {},

        //         }
        //     )
        // }
        // return workspace_controller.sendCommand(`equipment:create`, res)
    }

    updateParams(names: string[]) {
        let res: { name: string, params: Record<string, AllParamTypes> }[] = []
        for (const name of names) {
            if (!(name in this.#equipments)) {
                beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
                return
            }
            res.push({
                name,
                params: this.#equipments[name].temp_params
            })
        }
        return workspace_controller.sendCommand(`equipment:update_params`, res)
    }

    remove(names: string[]) {
        let res: string[] = []
        for (const name of names) {
            if (!(name in this.#equipments)) {
                beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
                continue
            }
            res.push(name)
        }
        return workspace_controller.sendCommand(`equipment:remove`, res)
    }

    reload(name: string) {
        const save: Instance = JSON.parse(JSON.stringify({ ...this.#equipments[name] }))

        console.log({ save })

        const remove_update_params_callback = workspace_controller.registerCallback(`equipment:update_params`, async (instances: { name: string, params: Prettify<Instance["params"]> }[]) => {

            for (const { name } of instances) {
                if (save.name !== name) continue

                await remove_update_params_callback()
                this.assignTempParams(name, save.temp_params)
                break
            }

        })

        const remove_create_callback = workspace_controller.registerCallback(`equipment:create`, async (instances: ConcInstance[]) => {
            if (!instances.map(({ name }) => name).includes(save.name)) return

            await remove_create_callback()

            if (JSON.stringify(save.params) ===
                JSON.stringify(this.#equipments[save.name].params)) {
                this.assignTempParams(name, save.temp_params)
                await tick()
                console.log($state.snapshot(this.#equipments[save.name].params))
                await remove_update_params_callback()
                return
            }

            this.assignTempParams(save.name, save.params)
            await tick()
            this.updateParams([save.name])
            return


        })

        const remove_remove_callback = workspace_controller.registerCallback(`equipment:remove`, async (names: string[]) => {
            if (!names.includes(save.name)) return

            await remove_remove_callback()
            // this.create([save])
        })

        if (!(name in this.#equipments)) {
            beinn_log_controller.append(`ERROR Instance with name ${name} does not exist`)
            return
        }

        this.remove([name])
    }



    getSave() {
        const res: Record<string, Instance> = {}
        for (const instance of Object.values(this.#equipments))
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

        const remove_update_params_callback = workspace_controller.registerCallback(`equipment:update_params`, async (instances: { name: string, params: Prettify<Instance["params"]> }[], id: string) => {
            if (id !== request_id.value) return
            await remove_update_params_callback()

            for (const { name } of instances) {
                await remove_update_params_callback()
                this.assignTempParams(name, save[name].temp_params)
            }
        })

        const remove_create_callback = workspace_controller.registerCallback(`equipment:create`, async (instances: ConcInstance[], id: string) => {
            if (id !== request_id.value) return

            await remove_create_callback()

            for (const instance of instances) {

                if (JSON.stringify(save[instance.name].params) ===
                    JSON.stringify(this.#equipments[instance.name].temp_params))
                    return

                this.assignTempParams(instance.name, save[instance.name].params)

            }

            await tick()
            request_id.value = this.updateParams(instances.map(({ name }) => name)) ?? ""
        })

        // request_id.value = this.create(Object.values(save).map(({ name, module, cls }) => ({ name, module, cls }))) ?? ""
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
                    // case "instance.equipment": if (!((param as InstanceEquipmentParam).name in equipment_controller.instances)) return

                }

                if (obj[key].type === "instance.equipment")
                    obj[key].name = (param as InstanceEquipmentParam).name
                else
                    obj[key].value = (param as Exclude<SimpleParamType, { type: "instance.equipment" }>).value
            }
        }


        for (const instance of Object.values(this.#equipments)) {
            if (instance.name !== name)
                continue

            for (const [key, value] of Object.entries(params)) {
                if (value.type === "composite")
                    for (const [key, deep_value] of Object.entries(value.children))
                        assignParam(instance.temp_params, key, deep_value)
                else
                    assignParam(instance.temp_params, key, value)

            }
        }
    }

    reset() {
        this.#equipments = {}
        this.imports = []
        this.temp_module = ""
        this.temp_cls = ""
        this.temp_name = ""
    }
}

export const equipment_controller = $state(new EquipmentController())