import { qoslabappCreateEE, qoslabappGetEEParams, qoslabappRemoveEE, qoslabappSetEEParams } from "$services/qoslabapp.svelte"
import { applicationError, userError, type AllParamTypes, type EET, type EEType, type ModuleCls } from "qoslab-shared"
import { gstore } from "./global.svelte"
import { tick } from "svelte"

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
    set module_cls(module_cls: ModuleCls) {
        // Check if module cls exists
        if (this.eetype === "equipment") {
            if (!gstore.workspace.equipments.moduleClsValid(module_cls))
                throw applicationError(`${this._id}: module ${module_cls.module} and class ${module_cls.cls} invalid.`)
        }

        if (this.eetype === "experiment") {
            if (!gstore.workspace.experiments.moduleClsValid(module_cls))
                throw applicationError(`${this._id}: module ${module_cls.module} and class ${module_cls.cls} invalid.`)
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
    set temp_params(params: Record<string, AllParamTypes>) {
        this.write_params(params, this._temp_params)
    }


    private write_params(params: Record<string, AllParamTypes>, target_params: Record<string, AllParamTypes>) {
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

                    // Check if theeetypeexists. Add if it is
                    if (this.eetype === "equipment") {
                        if (gstore.workspace.equipments.equipments[param.instance_id] !== undefined)
                            target_params[name].instance_id = param.instance_id
                    }
                    else if (this.eetype === "experiment") {
                        if (gstore.workspace.experiments.experiments[param.instance_id] !== undefined)
                            target_params[name].instance_id = param.instance_id
                    }

                    continue
                case "instance.experiment":
                    if (param.type !== target_params[name].type) continue

                    if (this.eetype === "equipment")
                        throw userError(`Equipment ${this._id}, param ${name}: Equipment shall only haveeetypeinstance params`)

                    // Only for expeirment
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
        // Create theeetypein qoslabapp and fetch initial params
        await qoslabappCreateEE(this.eetype, {
            id: this._id,
            module_cls: this._module_cls
        });

        const res = await qoslabappGetEEParams(this.eetype, { id: this._id })

        this.params = JSON.parse(JSON.stringify(res))
        this._temp_params = JSON.parse(JSON.stringify(res))
        this._created = true


        await tick()
        console.log(this)
    }

    async saveParams() {
        await qoslabappSetEEParams(this.eetype, { id: this._id, params: this._temp_params })
        this.params = JSON.parse(JSON.stringify(this._temp_params))
    }

    async remove() {
        const res = await qoslabappRemoveEE(this.eetype, { id: this._id });
        setTimeout(() => {
            if (this.eetype === "equipment")
                delete gstore.workspace.equipments.equipments[this._id]
            else delete gstore.workspace.experiments.experiments[this._id]
        })
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

