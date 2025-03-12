from ast import TypeVar
from typing import Literal

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


class SelectStrParam(BaseModel):
    type: Literal["select.str"]
    options: list[str]
    value: str


def select_strParam(options: list[str], default: int = 0) -> SelectStrParam:
    return {"type": "select.str", "options": options, "value": options[default]}


class SelectIntParam(BaseModel):
    type: Literal["select.int"]
    options: list[int]
    value: int


def select_intParam(options: list[int], default: int = 0) -> SelectIntParam:
    return {"type": "select.int", "options": options, "value": options[default]}


class SelectFloatParam(BaseModel):
    type: Literal["select.float"]
    options: list[float]
    value: int


def select_floatParam(options: list[float], default: int = 0) -> SelectFloatParam:
    return {"type": "select.float", "options": options, "value": options[default]}


class IntParam(BaseModel):
    type: Literal["int"]
    suffix: str
    value: int


def intParam(default: int = 0, suffix: str = "") -> IntParam:
    return {"type": "int", "suffix": suffix, "value": default}


class FloatParam(BaseModel):
    type: Literal["float"]
    suffix: str
    value: float


def floatParam(default: float = 0.0, suffix: str = "") -> FloatParam:
    return {"type": "float", "suffix": suffix, "value": default}


class StrParam(BaseModel):
    type: Literal["str"]
    value: str


def strParam(default: str = "") -> StrParam:
    return {"type": "str", "value": default}


class BoolParam(BaseModel):
    type: Literal["bool"]
    value: bool


def boolParam(default: bool) -> BoolParam:
    return {"type": "bool", "value": default}


class InstanceEquipmentParam[T](GenericModel):
    type: Literal["instance.equipment"]
    instance_name: str
    instance: T | None = Field(exclude=True)


def instance_equipmentParam[T]() -> InstanceEquipmentParam[T]:
    return {"type": "instance.equipment", "instance_name": "", "instance": None}


class InstanceExperimentParam[T](GenericModel):
    type: Literal["instance.experiment"]
    instance_name: str
    instance: T | None = Field(exclude=True)


def instance_experimentParam[T]() -> InstanceExperimentParam[T]:
    return {"type": "instance.experiment", "instance_name": "", "instance": None}


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


class CompositeParam(BaseModel):
    type: Literal["composite"]
    children: dict[str, AllParamTypes]
