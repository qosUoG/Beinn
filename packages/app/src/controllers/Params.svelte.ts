import type { Instance } from "./_ee.svelte"
import { equipment_controller } from "./equipment.svelte"
import { log_controller } from "./log.svelte"

export type SelectStrParam = {
    type: "select.str"
    options: string[]
    value: string
    required: boolean
}

export type SelectIntParam = {
    type: "select.int"
    options: number[]
    value: number
    required: boolean
}

export type SelectFloatParam = {
    type: "select.float"
    options: number[]
    value: number
    required: boolean
}

export type IntParam = {
    type: "int"
    suffix?: string
    value: number
    required: boolean
}


export type FloatParam = {
    type: "float"
    suffix?: string
    value: number
    required: boolean
}


export type StrParam = {
    type: "str"
    value: string
    required: boolean
}

export type BoolParam = {
    type: "bool"
    value: boolean
    required: boolean
}

export type InstanceEquipmentParam = {
    type: "instance.equipment"
    value: string | null
    required: boolean
}

export type RuntimeEquipmentParam = {
    type: "instance.equipment"
    value: string
    instance: Instance
    required: boolean
} | {
    type: "instance.equipment"
    value: null
    instance: undefined
    required: boolean
}



// export type  InstanceExperimentParam  ={
//     type: "instance.experiment"
//     name: string
// }

export type SimpleParamType = (
    SelectStrParam | SelectFloatParam | SelectIntParam | IntParam | FloatParam | StrParam | BoolParam |
    InstanceEquipmentParam
    //  | InstanceExperimentParam
)


export type CompositeParam = {
    type: "composite"
    children: Record<string, SimpleParamType>
}

export type AllParamTypes = SimpleParamType | CompositeParam

export type RuntimeSimpleParamType = (
    SelectStrParam | SelectFloatParam | SelectIntParam | IntParam | FloatParam | StrParam | BoolParam |
    RuntimeEquipmentParam
    //  | InstanceExperimentParam
)

export type RuntimeCompositeParam = {
    type: "composite"
    children: Record<string, RuntimeSimpleParamType>
}

export type RuntimeAllParamTypes = RuntimeSimpleParamType | RuntimeCompositeParam




export function runtime2Save(params: Record<string, RuntimeAllParamTypes>) {
    const convert
        : (_: RuntimeSimpleParamType) => SimpleParamType
        = (param: RuntimeSimpleParamType) => {
            switch (param.type) {
                case "instance.equipment":
                    return {
                        type: "instance.equipment",
                        value: param.value,
                        required: param.required,
                    }

                default:
                    return param
            }
        }


    let res: Record<string, AllParamTypes> = {}
    for (const [key, param] of Object.entries(params)) {
        switch (param.type) {
            case "composite":
                let t_res: Record<string, SimpleParamType> = {}
                for (const [c_key, c_param] of Object.entries(param.children)) {
                    t_res[c_key] = convert(c_param)
                }
                res[key] = {
                    type: "composite",
                    children: t_res
                }
                break
            default:
                res[key] = convert(param)
        }

    }
    return res
}

export function save2Runtime(params: Record<string, AllParamTypes>) {

    const convert
        : (_: SimpleParamType) => RuntimeSimpleParamType
        = (param: SimpleParamType) => {
            switch (param.type) {
                case "instance.equipment":

                    if (!param.value) return {
                        type: "instance.equipment",
                        value: null,
                        required: param.required,
                        instance: undefined
                    }


                    const equipment = equipment_controller.equipments.find(e => e.name === param.value)
                    if (equipment === undefined) {
                        log_controller.appendError(`Cannot assign equipment param to ${param.value}: equipment not found`)
                        return {
                            type: "instance.equipment",
                            value: null,
                            required: param.required,
                            instance: undefined
                        }
                    }
                    return {
                        type: "instance.equipment",
                        value: param.value,
                        required: param.required,
                        instance: equipment
                    }

                default:
                    return param
            }
        }

    let res: Record<string, RuntimeAllParamTypes> = {}
    for (const [key, param] of Object.entries(params)) {
        switch (param.type) {
            case "composite":
                let t_res: Record<string, RuntimeSimpleParamType> = {}

                for (const [c_key, c_param] of Object.entries(param.children)) {
                    t_res[c_key] = convert(c_param)
                }
                res[key] = {
                    type: "composite",
                    children: t_res
                }
                break
            default:
                res[key] = convert(param)
        }
    }
    return res
}