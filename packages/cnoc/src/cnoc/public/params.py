from typing import cast
from .equipment import EquipmentABC
from . import _params

type _SimpleParamType = (
    _params.SelectStrParam
    | _params.SelectFloatParam
    | _params.SelectIntParam
    | _params.IntParam
    | _params.FloatParam
    | _params.StrParam
    | _params.BoolParam
    | _params.InstanceEquipmentParam[EquipmentABC]
)


class P:
    @classmethod
    def Int(cls):
        return _params.IntParam

    @classmethod
    def Float(cls):
        return _params.FloatParam

    @classmethod
    def Str(cls):
        return _params.StrParam

    @classmethod
    def Bool(cls):
        return _params.BoolParam

    @classmethod
    def Equipment[T: EquipmentABC](cls):
        return _params.InstanceEquipmentParam[T]

    @classmethod
    def Composite[T: dict[str, _SimpleParamType]](cls):
        return _params.CompositeParam[T]

    class Select:
        @classmethod
        def Str(cls):
            return _params.SelectStrParam

        @classmethod
        def Int(cls):
            return _params.SelectIntParam

        @classmethod
        def Float(cls):
            return _params.SelectFloatParam


class p:
    @classmethod
    def int(cls, default: int = 0, suffix: str = ""):
        return _params.IntParam(default, suffix)

    @classmethod
    def float(cls, default: float = 0.0, suffix: str = ""):
        return _params.FloatParam(default, suffix)

    @classmethod
    def str(cls, default: str = ""):
        return _params.StrParam(default)

    @classmethod
    def boolean(cls, default: bool = False):
        return _params.BoolParam(default)

    @classmethod
    def equipment[T: EquipmentABC](cls):
        return _params.InstanceEquipmentParam[T]()

    @classmethod
    def composite[T: dict[str, _SimpleParamType]](
        cls, children: dict[str, _SimpleParamType]
    ):
        return _params.CompositeParam[T](cast(T, children))

    class select:
        @classmethod
        def str(cls, options: list[str], value: str | None = None):
            return _params.SelectStrParam(options, value)

        @classmethod
        def int(cls, options: list[int], value: int | None = None):
            return _params.SelectIntParam(options, value)

        @classmethod
        def float(cls, options: list[float], value: float | None = None):
            return _params.SelectFloatParam(options, value)
