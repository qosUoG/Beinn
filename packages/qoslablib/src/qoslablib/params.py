from abc import ABC
from dataclasses import dataclass
from typing import Literal, override
from pydantic import BaseModel


class QosParam[T: BaseModel](ABC):
    def toBaseModel(self) -> T:
        # This function should return a BaseModel
        raise NotImplementedError


@dataclass
class SelectStrParam(QosParam):
    type: Literal["select.str"]
    options: list[str]
    value: str

    class Model(BaseModel):
        type: Literal["select.str"]
        options: list[str]
        value: str

    def __init__(self, options: list[str], default: int = 0):
        self.type = "select.str"
        self.options = options
        self.value = options[default]

    @override
    def toBaseModel(self) -> Model:
        return self.Model(type=self.type, options=self.options, value=self.value)


class SelectIntParam(QosParam):
    type: Literal["select.int"]
    options: list[int]
    value: int

    class Model(BaseModel):
        type: Literal["select.int"]
        options: list[int]
        value: int

    def __init__(self, options: list[int], default: int = 0):
        self.type = "select.int"
        self.options = options
        self.value = options[default]

    @override
    def toBaseModel(self) -> Model:
        return self.Model(type=self.type, options=self.options, value=self.value)


class SelectFloatParam:
    type: Literal["select.float"]
    options: list[float]
    value: int

    class Model(BaseModel):
        type: Literal["select.float"]
        options: list[float]
        value: float

    def __init__(self, options: list[float], default: int = 0):
        self.type = "select.float"
        self.options = options
        self.value = options[default]

    @override
    def toBaseModel(self) -> Model:
        return self.Model(type=self.type, options=self.options, value=self.value)


class IntParam:
    type: Literal["int"]
    suffix: str
    value: int

    class Model(BaseModel):
        type: Literal["int"]
        suffix: str
        value: int

    def __init__(self, default: int = 0, suffix: str = ""):
        self.type = "int"
        self.suffix = suffix
        self.default = default

    @override
    def toBaseModel(self) -> Model:
        return self.Model(type=self.type, suffix=self.suffix, value=self.value)


class FloatParam:
    type: Literal["float"]
    suffix: str
    value: float

    class Model(BaseModel):
        type: Literal["float"]
        suffix: str
        value: float

    def __init__(self, default: float = 0, suffix: str = ""):
        self.type = "float"
        self.suffix = suffix
        self.default = default

    @override
    def toBaseModel(self) -> Model:
        return self.Model(type=self.type, suffix=self.suffix, value=self.value)


class StrParam:
    type: Literal["str"]
    value: str

    class Model(BaseModel):
        type: Literal["str"]
        value: str

    def __init__(self, default: str = 0):
        self.type = "str"
        self.default = default

    @override
    def toBaseModel(self) -> Model:
        return self.Model(type=self.type, value=self.value)


class BoolParam:
    type: Literal["bool"]
    value: bool

    class Model(BaseModel):
        type: Literal["bool"]
        value: bool

    def __init__(self, default: bool = 0):
        self.type = "bool"
        self.default = default

    @override
    def toBaseModel(self) -> Model:
        return self.Model(type=self.type, value=self.value)


class InstanceEquipmentParam[T]:
    type: Literal["instance.equipment"]
    instance_name: str | None
    instance: T | None

    class Model(BaseModel):
        type: Literal["instance.equipment"]
        instance_name: str

    def __init__(self):
        self.type = "instance.equipment"
        self.instance_name = None
        self.instance = None

    @override
    def toBaseModel(self) -> Model:
        return self.Model(type=self.type, instance_name=self.instance_name)


class InstanceExperimentParam[T]:
    type: Literal["instance.experiment"]
    instance_name: str | None
    instance: T | None

    class Model(BaseModel):
        type: Literal["instance.experiment"]
        instance_name: str

    def __init__(self):
        self.type = "instance.experiment"
        self.instance_name = None
        self.instance = None

    @override
    def toBaseModel(self) -> Model:
        return self.Model(type=self.type, instance_name=self.instance_name)


type AllParamTypes = (
    SelectStrParam
    | SelectFloatParam
    | SelectIntParam
    | IntParam
    | FloatParam
    | StrParam
    | BoolParam
    | CompositeParam
    | InstanceEquipmentParam
    | InstanceExperimentParam
)

type Params = dict[str, AllParamTypes]


class CompositeParam:
    type: Literal["composite"]
    children: Params
