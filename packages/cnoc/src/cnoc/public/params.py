from dataclasses import field
from enum import Enum
from typing import Any, Iterable
from .equipment import EquipmentABC
from . import _params
from _typeshed import DataclassInstance


class p:
    @classmethod
    def int(cls, default: int = 0, suffix: str = ""):
        return field(default=_params.Int(default, suffix))

    @classmethod
    def float(cls, default: float = 0.0, suffix: str = ""):
        return field(default=_params.Float(default, suffix))

    @classmethod
    def str(cls, default: str = ""):
        return field(default=_params.Str(default))

    @classmethod
    def boolean(cls, default: bool = True):
        return field(default=_params.Bool(default))

    class composite[T: type[DataclassInstance]]:
        @classmethod
        def of(cls, children: T):
            return field(default=children())

    class equipment[T: EquipmentABC[Any]]:
        @classmethod
        def instance(cls):
            return field(default=_params.Equipment[T]())

    class select:
        @classmethod
        def str(cls, options: Iterable[str], default: str | None = None):
            return field(default=_params.Select.Str(list(options), default))

        @classmethod
        def enum(cls, default: Enum):
            return field(
                default=_params.Select.Str(
                    list(default.__class__.__members__.keys()), default.name
                )
            )

        @classmethod
        def int(cls, options: Iterable[int], default: int | None = None):
            return field(default=_params.Select.Int(list(options), default))

        @classmethod
        def float(cls, options: Iterable[float], default: float | None = None):
            return field(default=_params.Select.Float(list(options), default))
