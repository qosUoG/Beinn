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

type Bool = BoolParam
type Int = IntParam
type Float = FloatParam
type Str = StrParam
type Equipment = InstanceEquipmentParam[EquipmentABC]
type Composite = CompositeParam
type SelectStr = SelectStrParam
type SelectInt = SelectIntParam
type SelectFloat = SelectFloatParam

type AllParams = (
    SelectStrParam
    | SelectFloatParam
    | SelectIntParam
    | IntParam
    | FloatParam
    | StrParam
    | BoolParam
    | InstanceEquipmentParam[EquipmentABC]
)


class p:
    @classmethod
    def int(cls, default: int = 0, suffix: str = "", required: bool = False):
        return IntParam(default, suffix, required)

    @classmethod
    def float(cls, default: float = 0.0, suffix: str = "", required: bool = False):
        return FloatParam(default, suffix, required)

    @classmethod
    def str(cls, default: str = "", required: bool = False):
        return StrParam(default, required)

    @classmethod
    def boolean(cls, default: bool = False, required: bool = False):
        return BoolParam(default, required)

    @classmethod
    def equipment(cls, required: bool = False):
        return InstanceEquipmentParam(required)

    @classmethod
    def composite(cls, children: dict[str, AllParams]):
        return CompositeParam(children)

    class Select:
        @classmethod
        def str(
            cls, options: list[str], value: str | None = None, required: bool = False
        ):
            return SelectStrParam(options, value, required)

        @classmethod
        def int(
            cls, options: list[int], value: int | None = None, required: bool = False
        ):
            return SelectIntParam(options, value, required)

        @classmethod
        def float(
            cls,
            options: list[float],
            value: float | None = None,
            required: bool = False,
        ):
            return SelectFloatParam(options, value, required)
