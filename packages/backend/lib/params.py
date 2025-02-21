from typing import Literal, TypedDict


class SelectParam(TypedDict):
    type: Literal["select"]
    options: list[str]


class IntParam(TypedDict):
    type: Literal["int"]
    suffix: str | None
    value: int


class FloatParam(TypedDict):
    type: Literal["float"]
    suffix: str | None
    value: float


class StrParam(TypedDict):
    type: Literal["str"]
    value: str


class BoolParam(TypedDict):
    type: Literal["bool"]
    value: bool


type AllParamTypes = (
    SelectParam | IntParam | FloatParam | StrParam | BoolParam | CompositeParam
)


class CompositeParam(TypedDict):
    type: Literal["composite"]
    children: dict[str, "AllParamTypes"]
