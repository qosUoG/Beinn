
export interface SelectStrParam {
    type: "select.str"
    options: string[]
    selection: number
}

export interface SelectIntParam {
    type: "select.int"
    options: number[]
    selection: number
}

export interface SelectFloatParam {
    type: "select.float"
    options: number[]
    selection: number
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

export interface InstanceParam {
    type: "instance"
    instance_name: string
    instance: string
}

export type AllParamTypes = (
    SelectStrParam | SelectFloatParam | SelectIntParam | IntParam | FloatParam | StrParam | BoolParam | CompositeParam | InstanceParam
)


export interface CompositeParam {
    type: "composite"
    children: Record<string, AllParamTypes>
}