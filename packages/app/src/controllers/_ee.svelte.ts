import { deepCopy, shell, type Prettify } from "$lib/utils"
import { runtime2Save, save2Runtime, type AllParamTypes, type RuntimeAllParamTypes, type RuntimeEquipmentParam, type SelectFloatParam, type SelectStrParam } from "./params.svelte"
import { dependency_controller } from "./dependency.svelte"
import { workspace_controller } from "./workspace.svelte"
import { tick } from "svelte"
import { equipment_controller } from "./equipment.svelte"
import { log_controller } from "./log.svelte"


export type Imports = { module: string, cls: string }[]

export type ConcInstance = {
    module: string,
    cls: string,
    params: Record<string, AllParamTypes | Record<string, AllParamTypes>>,
}

export type InstanceSave = {
    name: string;
    module: string;
    cls: string;
    params: Record<string, AllParamTypes | Record<string, AllParamTypes>>;
    param_opens: boolean;
    composite_opens: Record<string, boolean>;
}

export class Instance {
    initialized: boolean = $state(false)

    module: string
    cls: string

    params: Record<string, RuntimeAllParamTypes | Record<string, RuntimeAllParamTypes>> = $state({})

    name: string
    temp_name: string

    param_opens: boolean = $state(true)
    composite_opens: Record<string, boolean> = $state({})
    reloading: boolean = $state(false)

    constructor(module: string, cls: string, name: string = "",
    ) {
        this.module = $state(module)
        this.cls = $state(cls)
        this.name = $state(name)
        this.temp_name = $state(name)
    }

    async initialize() {
        let res
        try {
            res = await this.getParams()
        } catch (e) {
            return
        }
        if (res === undefined) return

        this.params = save2Runtime(res.params)

        await tick()


        for (const [key, value] of Object.entries(this.params))
            if (!("type" in value) && this.composite_opens[key] === undefined)
                this.composite_opens[key] = true

        this.initialized = true
    }

    async reload() {
        this.reloading = true
        await tick()

        const temp: {
            params: Record<string, RuntimeAllParamTypes | Record<string, RuntimeAllParamTypes>>,
            composite_opens: Record<string, boolean>,
        } = deepCopy({
            params: this.params,
            composite_opens: this.composite_opens,
        })

        // Get the default params list of the instance
        const res = await this.getParams()

        if (res === undefined) {
            this.reloading = false
            return
        }

        this.params = save2Runtime(res.params)


        await tick()

        await this.assignParams(temp.params)

        await tick()

        // Remove composite_opens keys that are not in the new params
        for (const key of Object.keys(this.composite_opens))
            if (!(key in this.params))
                delete this.composite_opens[key]

        await tick()

        // Add composite_opens keys that are in the new params
        for (const [key, value] of Object.entries(this.params))
            if (!("type" in value) && this.composite_opens[key] === undefined)
                this.composite_opens[key] = true

        this.reloading = false
    }

    async getParams() {

        const { stdout, code } = await shell({ fn: "uv", cmd: ["run", "params", this.module, this.cls], description: `Loading ${this.module}.${this.cls}`, cwd: workspace_controller.path! })
        if (code !== 0) return

        return JSON.parse(stdout) as ConcInstance
    }



    async assignParams(params: Record<string, RuntimeAllParamTypes | Record<string, RuntimeAllParamTypes>>) {
        const assignParam = (obj: Record<string, RuntimeAllParamTypes>, key: string, param: AllParamTypes) => {
            if (!(key in obj) || obj[key].type !== param.type) return

            switch (param.type) {
                case "instance.equipment": {
                    if (!param.value) {
                        (obj[key] as RuntimeEquipmentParam).value = null;
                        (obj[key] as RuntimeEquipmentParam).instance = undefined
                        return
                    }


                    const equipment = equipment_controller.equipments.find(e => e.name === param.value)
                    if (equipment === undefined) {
                        log_controller.appendError(`Cannot assign param ${key} to ${param.value}: equipment not found`);
                        (obj[key] as RuntimeEquipmentParam).value = null;
                        (obj[key] as RuntimeEquipmentParam).instance = undefined;
                        return
                    }


                    (obj[key] as RuntimeEquipmentParam).value = param.value;
                    (obj[key] as RuntimeEquipmentParam).instance = equipment
                    return
                }
                case "select.str": {
                    if (!(obj[key] as SelectStrParam).options.includes(param.value))
                        (obj[key] as SelectStrParam).value = (obj[key] as SelectStrParam).options[0]
                    else (obj[key] as SelectStrParam).value = param.value
                    return
                }
                case "select.float":
                case "select.int": {
                    if (!(obj[key] as SelectFloatParam).options.includes(param.value as number))
                        (obj[key] as SelectFloatParam).value = (obj[key] as SelectFloatParam).options[0]
                    else (obj[key] as SelectFloatParam).value = param.value
                    return
                }

                default: {
                    obj[key].value = param.value
                }
            }
        }

        for (const [key, param] of Object.entries(params)) {
            if (!("type" in param)) {
                for (const [_key, _param] of Object.entries(param))
                    assignParam(this.params[key] as Record<string, RuntimeAllParamTypes>, _key, _param)
                continue
            }

            assignParam(this.params as Record<string, RuntimeAllParamTypes>, key, param as AllParamTypes)


        }
    }

    toSave(): InstanceSave {
        return $state.snapshot({
            name: this.name,
            module: this.module,
            cls: this.cls,
            params: runtime2Save(this.params),
            param_opens: this.param_opens,
            composite_opens: this.composite_opens,
        })
    }
}


export abstract class EEBaseController {
    imports: Imports = $state([])
    eetype: "equipment" | "experiment"

    constructor(eetype: "equipment" | "experiment") {
        this.eetype = eetype
    }

    reset() {
        this.imports = []
    }

    async updateImports() {
        const { stdout, code } = await shell({
            fn: "uv",
            cmd: ["run", "imports", this.eetype, ...dependency_controller.has_driver_package_names], description: `Loading available ${this.eetype} modules`,
            cwd: workspace_controller.path!,
        })


        if (code !== 0) return

        this.imports = JSON.parse(stdout) as Imports
    }
}