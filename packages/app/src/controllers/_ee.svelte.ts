import { shell, type Prettify } from "$lib/utils"
import type { AllParamTypes, SelectFloatParam, SelectStrParam, SimpleParamType } from "./params.svelte"
import { dependency_controller } from "./dependency.svelte"
import { workspace_controller } from "./workspace.svelte"
import { tick } from "svelte"
import { equipment_controller } from "./equipment.svelte"
import { log_controller } from "./log.svelte"


export type Imports = { module: string, cls: string }[]

export type ConcInstance = {
    module: string,
    cls: string,
    params: Record<string, AllParamTypes>,
}

export type InstanceSave = {
    name: string;
    module: string;
    cls: string;
    params: Record<string, AllParamTypes>;
    param_opens: boolean;
    composite_opens: Record<string, boolean>;
}

export class Instance {
    initialized: boolean = $state(false)

    module: string
    cls: string

    params: Record<string, AllParamTypes> = $state({})

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
        const res = await this.getParams()
        if (res === undefined) return

        this.params = res.params

        await tick()

        for (const [key, value] of Object.entries(this.params))
            if (value.type === "composite" && this.composite_opens[key] === undefined)
                this.composite_opens[key] = true

        this.initialized = true
    }

    async reload() {
        this.reloading = true
        await tick()

        const save: {
            params: Record<string, AllParamTypes>,
            composite_opens: Record<string, boolean>,
        } = JSON.parse(JSON.stringify({
            params: this.params,
            composite_opens: this.composite_opens,
        }))

        // Get the default params list of the instance
        const res = await this.getParams()

        if (res === undefined) {
            this.reloading = false
            return
        }

        this.params = res.params

        await tick()

        this.assignParams(save.params)

        await tick()

        // Remove composite_opens keys that are not in the new params
        for (const key of Object.keys(this.composite_opens))
            if (!(key in this.params))
                delete this.composite_opens[key]

        await tick()

        // Add composite_opens keys that are in the new params
        for (const [key, value] of Object.entries(this.params))
            if (value.type === "composite" && this.composite_opens[key] === undefined)
                this.composite_opens[key] = true

        this.reloading = false
    }

    async getParams() {

        const { stdout, code } = await shell({ fn: "uv", cmd: ["run", "params", this.module, this.cls], description: `Loading ${this.module}.${this.cls}`, cwd: workspace_controller.path! })
        if (code !== 0) return

        return JSON.parse(stdout) as ConcInstance
    }

    async assignParams(params: Prettify<Instance["params"]>) {
        const assignParam = (obj: Prettify<Exclude<Instance["params"], "composite">>, key: string, param: SimpleParamType) => {
            if (!(key in obj) || obj[key].type !== param.type) return

            switch (param.type) {
                case "instance.equipment": {
                    if (equipment_controller.equipment_names.includes(param.value))
                        obj[key].value = param.value

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

            if (param.type === "composite") {
                if (this.params[key]?.type !== "composite") continue

                for (const [child_key, child_param] of Object.entries(param.children))
                    assignParam(this.params[key].children, child_key, child_param)
            }
            else
                assignParam(this.params, key, param)
        }
    }

    toSave(): InstanceSave {
        return $state.snapshot({
            name: this.name,
            module: this.module,
            cls: this.cls,
            params: this.params,
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