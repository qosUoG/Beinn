
import type { ModuleCls } from "./dependency.svelte"


import { tick } from "svelte"
import type { AllParamTypes } from "./params.svelte"
import { beginProcedure, capitalise } from "$lib/utils"
import { workspace } from "./workspace.svelte"
import { meallCreateEE_throwable, meallGetEEParams_throwable, meallRemoveEE_throwable, meallSetEEParams_throwable } from "$lib/meall.svelte"

export type Availables = { modules: string[], cls: string }[]

/* EE Base Type */
export type EEType = "equipment" | "experiment"

export type EET = {
    id: string
    created: boolean
    module_cls: ModuleCls

    // The following may exist even created
    // This is because the EE may be in save but failed to setup when loading workspace
    name: string
    params: Record<string, AllParamTypes>
    temp_params: Record<string, AllParamTypes>
}

export abstract class EE {
    private _id: string
    get id() {
        return this._id
    }
    protected _created: boolean = $state(false)
    get created() {
        return this._created
    }
    private _module_cls: ModuleCls = $state({ module: "", cls: "" })
    get module_cls() {
        return this._module_cls
    }

    set module_cls_throwable(module_cls: ModuleCls) {
        // Check if module cls exists
        if (this.eetype === "equipment") {
            if (!workspace.equipments.moduleClsValid(module_cls))
                throw `${this._id}: module ${module_cls.module} and class ${module_cls.cls} invalid.`
        }

        if (this.eetype === "experiment") {
            if (!workspace.experiments.moduleClsValid(module_cls))
                throw `${this._id}: module ${module_cls.module} and class ${module_cls.cls} invalid.`
        }

        this._module_cls = module_cls
    }

    private eetype: EEType


    // The following may exist even created = false,
    // This is because the EE may be in save but failed to setup when loading workspace
    name: string = $state("")
    protected params: Record<string, AllParamTypes> = $state({})


    private _temp_params: Record<string, AllParamTypes> = $state({})
    get temp_params() {
        return this._temp_params
    }
    set temp_params_throwable(params: Record<string, AllParamTypes>) {
        this.write_params_throwable(params, this._temp_params)
    }


    private write_params_throwable(params: Record<string, AllParamTypes>, target_params: Record<string, AllParamTypes>) {
        // Need to check all params actually valid in terms of the param type and the corresponding key
        for (const [name, param] of Object.entries(params)) {
            // if name is not found, directly skip it
            if (target_params[name] === undefined) continue

            // Skip if param type does not equal
            switch (target_params[name].type) {
                case "select.str":
                case "select.float":
                case "select.int":
                    if (param.type !== target_params[name].type) continue

                    if ((target_params[name].options as unknown[]).includes(param.value))
                        target_params[name].value = param.value

                    continue
                case "int":
                case "float":
                    if (param.type !== target_params[name].type) continue

                    if (typeof param.value === "number")
                        target_params[name].value = param.value

                    continue
                case "str":
                    if (param.type !== target_params[name].type) continue

                    if (typeof param.value === "string")
                        target_params[name].value = param.value

                    continue
                case "bool":
                    if (param.type !== target_params[name].type) continue

                    if (typeof param.value === "boolean")
                        target_params[name].value = param.value

                    continue
                case "instance.equipment":
                    if (param.type !== target_params[name].type) continue

                    // Check if the equipment exists. Add if it is
                    if (workspace.equipments.equipments[param.instance_id] !== undefined)
                        target_params[name].instance_id = param.instance_id

                    continue
                case "instance.experiment":
                    if (param.type !== target_params[name].type) continue

                    if (this.eetype === "equipment")
                        throw `Equipment ${this._id}, param ${name}: Equipment shall only have instance.equipment params`

                    // Only for expeirment
                    if (workspace.experiments.experiments[param.instance_id] !== undefined)
                        target_params[name].instance_id = param.instance_id



            }
        }
    }


    private _shall_delete: boolean = $state(true)

    get shall_delete() {
        return this._shall_delete
    }

    constructor(id: string, eetype: EEType, name?: string) {
        this._id = id
        this.eetype = eetype
        this.name = name ?? ""
    }

    async create() {
        const { step, completed, unhandled } = await beginProcedure(`CREATE ${capitalise(this.eetype)}`)

        try {
            // Create the eetype in meall and fetch initial params
            await step(`Create ${this.eetype} in meall`,
                async () => {
                    await meallCreateEE_throwable(this.eetype, {
                        id: this._id,
                        module_cls: this._module_cls
                    });

                })

            await step("Get Default Param",
                async () => {
                    const res = await meallGetEEParams_throwable(this.eetype, { id: this._id })

                    this.params = JSON.parse(JSON.stringify(res))
                    this._temp_params = JSON.parse(JSON.stringify(res))
                    this._created = true


                    await tick()
                })

            await completed()
        }
        catch (e) {
            await unhandled(e)
        }

    }

    async saveParams() {
        const { step, completed, unhandled } = await beginProcedure(`SET PARAM`)

        try {
            await step("Save params in meall",
                async () => {
                    await meallSetEEParams_throwable(this.eetype, { id: this._id, params: this._temp_params })
                    this.params = JSON.parse(JSON.stringify(this._temp_params))
                }
            )

            await completed()
        }
        catch (e) {
            await unhandled(e)
        }
    }

    async remove() {
        const { step, completed, unhandled } = await beginProcedure(`REMOVE ${this.eetype}`)

        try {
            await step(`Remove ${this.eetype} in meall`,
                async () => {
                    await meallRemoveEE_throwable(this.eetype, { id: this._id });
                    setTimeout(() => {
                        if (this.eetype === "equipment")
                            delete workspace.equipments.equipments[this._id]
                        else delete workspace.experiments.experiments[this._id]
                    })
                })

            await completed()
        }
        catch (e) {
            await unhandled(e)
        }
    }

    toSave() {
        return {
            id: this._id,
            created: this._created,
            module_cls: this._module_cls,
            name: this.name,
            params: this.params,
            temp_params: this._temp_params
        }
    }

    params_edited = $derived(this._created
        ? JSON.stringify(this._temp_params) !==
        JSON.stringify(this.params)
        : false)

    cancelTempParams() {
        this._temp_params = JSON.parse(
            JSON.stringify(this.params)
        );
    }


}

