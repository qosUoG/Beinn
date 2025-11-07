from dataclasses import field
from enum import Enum
from typing import Any, Iterable, Type
from . import _params
from ._utils import DataclassInstance


class P:
    class Select:
        Str = _params.Select.Str
        Int = _params.Select.Int
        Float = _params.Select.Float

    Str = _params.Str
    Int = _params.Int
    Float = _params.Float
    Bool = _params.Bool
    Equipment = _params.Equipment


class p:
    @classmethod
    def int(cls, default: int = 0, suffix: str = ""):
        return field(default_factory=lambda: _params.Int(default, suffix))

    @classmethod
    def float(cls, default: float = 0.0, suffix: str = ""):
        return field(default_factory=lambda: _params.Float(default, suffix))

    @classmethod
    def str(cls, default: str = ""):
        return field(default_factory=lambda: _params.Str(default))

    @classmethod
    def boolean(cls, default: bool = True):
        return field(default_factory=lambda: _params.Bool(default))

    @classmethod
    def equipment(cls):
        return field(default_factory=lambda: _params.Equipment[Any]())

    @classmethod
    def composite(cls, children: Type[DataclassInstance]):
        return field(default_factory=lambda: children())

    class select:
        @classmethod
        def str(cls, options: Iterable[str], default: str | None = None):
            return field(
                default_factory=lambda: _params.Select.Str(list(options), default)
            )

        @classmethod
        def enum(cls, default: Enum):
            return field(
                default_factory=lambda: _params.Select.Str(
                    list(default.__class__.__members__.keys()), default.name
                )
            )

        @classmethod
        def int(cls, options: Iterable[int], default: int | None = None):
            return field(
                default_factory=lambda: _params.Select.Int(list(options), default)
            )

        @classmethod
        def float(cls, options: Iterable[float], default: float | None = None):
            return field(
                default_factory=lambda: _params.Select.Float(list(options), default)
            )
