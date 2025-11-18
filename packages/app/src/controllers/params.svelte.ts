import type { Instance } from "./_ee.svelte"
import { equipment_controller } from "./equipment.svelte"
import { log_controller } from "./log.svelte"

export type SelectStrParam = {
    type: "select.str"
    options: string[]
    value: string
}

export type SelectIntParam = {
    type: "select.int"
    options: number[]
    value: number
}

export type SelectFloatParam = {
    type: "select.float"
    options: number[]
    value: number
}

export type IntParam = {
    type: "int"
    suffix?: string
    value: number
}


export type FloatParam = {
    type: "float"
    suffix?: string
    value: number
}


export type StrParam = {
    type: "str"
    value: string
}

export type BoolParam = {
    type: "bool"
    value: boolean
}

export type InstanceEquipmentParam = {
    type: "instance.equipment"
    value: string | null
}

export type RuntimeEquipmentParam = {
    type: "instance.equipment"
    value: string
    instance: Instance
} | {
    type: "instance.equipment"
    value: null
    instance: undefined
}

export type AllParamTypes = (
    SelectStrParam | SelectFloatParam | SelectIntParam | IntParam | FloatParam | StrParam | BoolParam |
    InstanceEquipmentParam
)

export type RuntimeAllParamTypes = (
    SelectStrParam | SelectFloatParam | SelectIntParam | IntParam | FloatParam | StrParam | BoolParam |
    RuntimeEquipmentParam
)

export function runtime2Save(params: Record<string, RuntimeAllParamTypes | Record<string, RuntimeAllParamTypes>>) {
    const convert
        : (_: RuntimeAllParamTypes) => AllParamTypes
        = (param: RuntimeAllParamTypes) => {
            switch (param.type) {
                case "instance.equipment":
                    return {
                        type: "instance.equipment",
                        value: param.value,

                    }

                default:
                    return param
            }
        }


    let res: Record<string, AllParamTypes | Record<string, AllParamTypes>> = {}
    for (const [key, param] of Object.entries(params)) {
        if ("type" in param) {
            res[key] = convert(param as RuntimeAllParamTypes)
            continue
        }
        let _res: Record<string, AllParamTypes> = {}
        for (const [_key, _param] of Object.entries(param))
            _res[_key] = convert(_param as RuntimeAllParamTypes)

        res[key] = _res
    }

    return res
}

export function save2Runtime(params: Record<string, AllParamTypes | Record<string, AllParamTypes>>) {

    const convert
        : (_: AllParamTypes) => RuntimeAllParamTypes
        = (param: AllParamTypes) => {
            switch (param.type) {
                case "instance.equipment":

                    if (!param.value) return {
                        type: "instance.equipment",
                        value: null,
                        instance: undefined
                    }


                    const equipment = equipment_controller.equipments.find(e => e.name === param.value)
                    if (equipment === undefined) {
                        log_controller.appendError(`Cannot assign equipment param to ${param.value}: equipment not found`)
                        return {
                            type: "instance.equipment",
                            value: null,
                            instance: undefined
                        }
                    }

                    return {
                        type: "instance.equipment",
                        value: param.value,
                        instance: equipment
                    }

                default:
                    return param
            }
        }

    let res: Record<string, RuntimeAllParamTypes | Record<string, RuntimeAllParamTypes>> = {}
    for (const [key, param] of Object.entries(params)) {
        if ("type" in param) {
            res[key] = convert(param as AllParamTypes)
            continue
        }

        let _res: Record<string, RuntimeAllParamTypes> = {}
        for (const [_key, _param] of Object.entries(param))
            _res[_key] = convert(_param as AllParamTypes)

        res[key] = _res

    }
    return res
}


export type ArchivedParams =
    | { value: number, suffix?: string }
    | { value: string | boolean }
    | { value: string, params: Record<string, ArchivedParams> }

