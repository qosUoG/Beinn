from typing import Any, Literal
from pydantic import BaseModel


class SelectStrParam(BaseModel):
    type: Literal["select.str"]
    options: list[str]
    selection: int


def select_str_param(options: list[str], selection: int = 0) -> SelectStrParam:
    return {"type": "select.str", "options": options, "selection": selection}


class SelectIntParam(BaseModel):
    type: Literal["select.int"]
    options: list[int]
    selection: int


def select_int_param(options: list[int], selection: int = 0) -> SelectIntParam:
    return {"type": "select.int", "options": options, "selection": selection}


class SelectFloatParam(BaseModel):
    type: Literal["select.float"]
    options: list[float]
    selection: int


def select_float_param(options: list[float], selection: int = 0) -> SelectFloatParam:
    return {"type": "select.float", "options": options, "selection": selection}


class IntParam(BaseModel):
    type: Literal["int"]
    suffix: str
    value: int


def int_param(default: int = 0, suffix: str = "") -> IntParam:
    return {"type": "int", "suffix": suffix, "value": default}


class FloatParam(BaseModel):
    type: Literal["float"]
    suffix: str
    value: float


def float_param(default: float = 0.0, suffix: str = "") -> FloatParam:
    return {"type": "float", "suffix": suffix, "value": default}


class StrParam(BaseModel):
    type: Literal["str"]
    value: str


def str_param(default: str = "") -> StrParam:
    return {"type": "str", "value": default}


class BoolParam(BaseModel):
    type: Literal["bool"]
    value: bool


def bool_param(default: bool) -> BoolParam:
    return {"type": "bool", "value": default}


class InstanceParam(BaseModel):
    type: Literal["instance"]
    instance_name: str
    instance: Any


def instance_param() -> InstanceParam:
    return {"type": "instance", "instance_name": "", "instance": ""}


type AllParamTypes = (
    SelectStrParam
    | SelectFloatParam
    | SelectIntParam
    | IntParam
    | FloatParam
    | StrParam
    | BoolParam
    | CompositeParam
    | InstanceParam
)


class CompositeParam(BaseModel):
    type: Literal["composite"]
    children: dict[str, "AllParamTypes"]
