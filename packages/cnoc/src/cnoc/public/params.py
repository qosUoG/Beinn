from .equipment import EquipmentABC
from ._params import (
    BoolParam,
    CompositeParam,
    FloatParam,
    InstanceEquipmentParam,
    IntParam,
    SelectFloatParam,
    SelectIntParam,
    SelectStrParam,
    StrParam,
)

type Param = (
    SelectStrParam
    | SelectFloatParam
    | SelectIntParam
    | IntParam
    | FloatParam
    | StrParam
    | BoolParam
    | InstanceEquipmentParam[EquipmentABC]
)


class Param:
    @classmethod
    def Int(cls, default: int = 0, suffix: str = "", required: bool = False):
        return IntParam(default, suffix, required)

    @classmethod
    def Float(cls, default: float = 0.0, suffix: str = "", required: bool = False):
        return FloatParam(default, suffix, required)

    @classmethod
    def Str(cls, default: str = "", required: bool = False):
        return StrParam(default, required)

    @classmethod
    def Bool(cls, default: bool = False, required: bool = False):
        return BoolParam(default, required)

    @classmethod
    def Equipment(cls, required: bool = False):
        return InstanceEquipmentParam(required)

    @classmethod
    def Composite(cls, children: dict[str, Param]):
        return CompositeParam(children)

    class Select:
        @classmethod
        def Str(
            cls, options: list[str], value: str | None = None, required: bool = False
        ):
            return SelectStrParam(options, value, required)

        @classmethod
        def Int(
            cls, options: list[int], value: int | None = None, required: bool = False
        ):
            return SelectIntParam(options, value, required)

        @classmethod
        def Float(
            cls,
            options: list[float],
            value: float | None = None,
            required: bool = False,
        ):
            return SelectFloatParam(options, value, required)
