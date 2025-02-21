
export interface SelectParam {
    type: "select"
    options: string[]
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

export type AllParamTypes = (
    SelectParam | IntParam | FloatParam | StrParam | BoolParam | CompositeParam
)


export interface CompositeParam {
    type: "composite"
    children: Record<string, AllParamTypes>
}