
export interface SelectStrParam {
    type: "select.str"
    options: string[]
    value: string
}

export interface SelectIntParam {
    type: "select.int"
    options: number[]
    value: number
}

export interface SelectFloatParam {
    type: "select.float"
    options: number[]
    value: number
}

export interface IntParam {
    type: "int"
    suffix?: string
    value: number
}


export interface FloatParam {
    type: "float"
    suffix?: string
    value: number
}


export interface StrParam {
    type: "str"
    value: string
}

export interface BoolParam {
    type: "bool"
    value: boolean
}

export interface InstanceEquipmentParam {
    type: "instance.equipment"
    instance_id: string
    instance: string
}

export interface InstanceExperimentParam {
    type: "instance.experiment"
    instance_id: string
    instance: string
}

export type AllParamTypes = (
    SelectStrParam | SelectFloatParam | SelectIntParam | IntParam | FloatParam | StrParam | BoolParam |
    //  CompositeParam |
    InstanceEquipmentParam | InstanceExperimentParam
)


// export interface CompositeParam {
//     type: "composite"
//     children: Record<string, AllParamTypes>
// }