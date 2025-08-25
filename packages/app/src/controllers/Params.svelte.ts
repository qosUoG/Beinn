export interface SelectStrParam {
    type: "select.str"
    options: string[]
    value: string
    required: boolean
}

export interface SelectIntParam {
    type: "select.int"
    options: number[]
    value: number
    required: boolean
}

export interface SelectFloatParam {
    type: "select.float"
    options: number[]
    value: number
    required: boolean
}

export interface IntParam {
    type: "int"
    suffix?: string
    value: number
    required: boolean
}


export interface FloatParam {
    type: "float"
    suffix?: string
    value: number
    required: boolean
}


export interface StrParam {
    type: "str"
    value: string
    required: boolean
}

export interface BoolParam {
    type: "bool"
    value: boolean
    required: boolean
}

export interface InstanceEquipmentParam {
    type: "instance.equipment"
    name: string
    required: boolean
}

// export interface InstanceExperimentParam {
//     type: "instance.experiment"
//     name: string
// }

export type SimpleParamType = (
    SelectStrParam | SelectFloatParam | SelectIntParam | IntParam | FloatParam | StrParam | BoolParam |
    InstanceEquipmentParam
    //  | InstanceExperimentParam
)

export interface CompositeParam {
    type: "composite"
    children: Record<string, SimpleParamType>
}

export type AllParamTypes = SimpleParamType | CompositeParam