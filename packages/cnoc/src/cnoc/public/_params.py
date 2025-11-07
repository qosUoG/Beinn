"""
Class of all parameter types

This module contains all types of parameter supported by the framework.

For examples of defining the type and the instance of params in equipment or
experiment, please refer to the example directory.

    * _QosParam - private base class for all param type for typesafety

    * SelectStrParam - multiselect param type with value of str type
    * SelectIntParam - multiselect param type with value of int type
    * SelectFloatParam - multiselect param type with value of float type

    * StrParam - param type with value of str type
    * IntParam - param type with value of int type
    * FloatParam - param type with value of float type
    * BoolParam - param type with value of bool type

    * InstanceEquipmentParam - param type with value implementing EquipmentABC type


"""

from dataclasses import InitVar, asdict, dataclass, field, fields
from _typeshed import DataclassInstance

from typing import (
    Any,
    ClassVar,
    Generic,
    Literal,
    TypedDict,
    cast,
    TypeVar,
)
from .equipment import EquipmentABC


class Select:
    @dataclass
    class Int:
        type: ClassVar[Literal["select.int"]] = "select.int"

        options: list[int]
        default: InitVar[int | None] = None

        value: int = field(init=False)

        def __post_init__(self, default: int | None):
            if default is not None and default in self.options:
                self.value = default

            else:
                self.value = self.options[0]

        class DictType(TypedDict):
            type: Literal["select.int"]
            options: list[int]
            value: int

        def toDict(self) -> DictType:
            return {"type": self.type, "options": self.options, "value": self.value}

        @classmethod
        def fromDict(cls, data: DictType):
            if data["type"] != cls.type:
                raise ValueError(f"Invalid type {data['type']} for {cls.type}")
            return cls(data["options"], data["value"])

        class SaveType(TypedDict):
            value: int

        def toSave(self) -> SaveType:
            return {"value": self.value}

    @dataclass
    class Float:
        type: ClassVar[Literal["select.float"]] = "select.float"

        options: list[float]
        default: InitVar[float | None] = None

        value: float = field(init=False)

        def __post_init__(self, default: float | None):
            if default is not None and default in self.options:
                self.value = default

            else:
                self.value = self.options[0]

        class DictType(TypedDict):
            type: Literal["select.float"]
            options: list[float]
            value: float

        def toDict(self) -> DictType:
            return {"type": self.type, "options": self.options, "value": self.value}

        @classmethod
        def fromDict(cls, data: DictType):
            if data["type"] != cls.type:
                raise ValueError(f"Invalid type {data['type']} for {cls.type}")
            return cls(data["options"], data["value"])

        class SaveType(TypedDict):
            value: float

        def toSave(self) -> SaveType:
            return {"value": self.value}

    @dataclass
    class Str:
        type: ClassVar[Literal["select.str"]] = "select.str"

        options: list[str]
        default: InitVar[str | None] = None

        value: str = field(init=False)

        def __post_init__(self, default: str | None):
            if default is not None and default in self.options:
                self.value = default

            else:
                self.value = self.options[0]

        class DictType(TypedDict):
            type: Literal["select.str"]
            options: list[str]
            value: str

        def toDict(self) -> DictType:
            return {"type": self.type, "options": self.options, "value": self.value}

        @classmethod
        def fromDict(cls, data: DictType):
            if data["type"] != cls.type:
                raise ValueError(f"Invalid type {data['type']} for {cls.type}")
            return cls(data["options"], data["value"])

        class SaveType(TypedDict):
            value: str

        def toSave(self) -> SaveType:
            return {"value": self.value}


@dataclass
class Int:
    type: ClassVar[Literal["int"]] = "int"

    value: int = field(default=0)
    suffix: str = field(default="")

    class DictType(TypedDict):
        type: Literal["int"]
        suffix: str
        value: int

    def toDict(self) -> DictType:
        return {"type": self.type, "suffix": self.suffix, "value": self.value}

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(data["value"], data["suffix"])

    class SaveType(TypedDict):
        value: int
        suffix: str

    def toSave(self) -> SaveType:
        return {"value": self.value, "suffix": self.suffix}


@dataclass
class Float:
    type: ClassVar[Literal["float"]] = "float"
    value: float = field(default=0.0)
    suffix: str = field(default="")

    class DictType(TypedDict):
        type: Literal["float"]
        suffix: str
        value: float

    def toDict(self) -> DictType:
        return {"type": self.type, "suffix": self.suffix, "value": self.value}

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")

        return cls(data["value"], data["suffix"])

    class SaveType(TypedDict):
        value: float
        suffix: str

    def toSave(self) -> SaveType:
        return {"value": self.value, "suffix": self.suffix}


@dataclass
class Str:
    type: ClassVar[Literal["str"]] = "str"
    value: str = field(default="")

    class DictType(TypedDict):
        type: Literal["str"]
        value: str

    def toDict(self) -> DictType:
        return {"type": self.type, "value": self.value}

    @classmethod
    def fromDict(cls, d: DictType):
        return cls(value=d["value"])

    class SaveType(TypedDict):
        value: str

    def toSave(self) -> SaveType:
        return {"value": self.value}


@dataclass
class Bool:
    type: ClassVar[Literal["bool"]] = "bool"
    value: bool = field(default=False)

    class DictType(TypedDict):
        type: Literal["bool"]
        value: bool

    def toDict(self) -> DictType:
        return {"type": self.type, "value": self.value}

    @classmethod
    def fromDict(cls, d: DictType):
        return cls(value=d["value"])

    class SaveType(TypedDict):
        value: bool

    def toSave(self) -> SaveType:
        return {"value": self.value}


_GenericEquipment = TypeVar("_GenericEquipment", bound=EquipmentABC)


@dataclass
class Equipment(Generic[_GenericEquipment]):
    type: ClassVar[Literal["instance.equipment"]] = "instance.equipment"

    value: str | None = field(default=None)
    instance: _GenericEquipment | None = field(default=None)

    class DictType(TypedDict):
        type: Literal["instance.equipment"]
        value: str | None

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "value": self.value if self.value else None,
        }

    @classmethod
    def fromDict(cls, data: DictType, equipments: dict[str, EquipmentABC]):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")

        if data["value"] is not None:
            if data["value"] not in equipments:
                raise ValueError(f"Equipment {data['value']} not found.")

            return cls(
                value=data["value"],
                instance=cast(_GenericEquipment, equipments[data["value"]]),
            )

        return cls()

    class SaveType(TypedDict):
        value: str | None
        params: dict[str, "AllParamSaveType"] | None

    def toSave(self) -> SaveType:
        if self.instance is None:
            return {"value": None, "params": None}
        assert hasattr(self.instance, "params")
        return {
            "value": self.value,
            "params": params2Dict(self.instance.params),  # type: ignore
        }


type AllParamType = (
    Select.Int
    | Select.Float
    | Select.Str
    | Int
    | Float
    | Str
    | Bool
    | Equipment[EquipmentABC]
)

type AllParamDictType = (
    Select.Int.DictType
    | Select.Float.DictType
    | Select.Str.DictType
    | Int.DictType
    | Float.DictType
    | Str.DictType
    | Bool.DictType
    | Equipment[EquipmentABC].DictType
)

type AllParamSaveType = (
    Select.Int.SaveType
    | Select.Float.SaveType
    | Select.Str.SaveType
    | Int.SaveType
    | Float.SaveType
    | Str.SaveType
    | Bool.SaveType
    | Equipment[EquipmentABC].SaveType
)


ParamsType = TypeVar("ParamsType", bound=type[DataclassInstance])


def params2Dict(params: Any):
    """
    Convert the params to a dictionary representation
    """

    return {k: cast(AllParamType, v).toDict() for k, v in asdict(params).items()}


def dict2Params(
    data: dict[str, AllParamDictType | dict[str, AllParamDictType]],
    equipments: dict[str, EquipmentABC],
    ParamsCls: ParamsType,
) -> ParamsType:
    """
    Convert the dictionary representation back to Params
    However this function does not set the instance of the params,
    i.e. the instance must be set after all instances are loaded
    """
    res = {}
    for k, v in data.items():
        if "type" not in v:
            fs = fields(ParamsCls)
            for f in fs:
                if f.name == k:
                    res[k] = dict2Params(
                        cast(
                            dict[str, AllParamDictType | dict[str, AllParamDictType]], v
                        ),
                        equipments,
                        cast(ParamsType, f.type),
                    )
                    break

        match v["type"]:
            case "bool":
                res[k] = Bool.fromDict(cast(Bool.DictType, v))
            case "float":
                res[k] = Float.fromDict(cast(Float.DictType, v))
            case "int":
                res[k] = Int.fromDict(cast(Int.DictType, v))
            case "str":
                res[k] = Str.fromDict(cast(Str.DictType, v))
            case "select.str":
                res[k] = Select.Str.fromDict(cast(Select.Str.DictType, v))
            case "select.int":
                res[k] = Select.Int.fromDict(cast(Select.Int.DictType, v))
            case "select.float":
                res[k] = Select.Float.fromDict(cast(Select.Float.DictType, v))
            case "instance.equipment":
                res[k] = Equipment.fromDict(cast(Equipment.DictType, v), equipments)
            case _:
                raise ValueError(f"Invalid type {v['type']}")

    return ParamsCls(**res)


def params2Save(params: DataclassInstance) -> dict[str, Any]:
    res: dict[str, AllParamSaveType | dict[str, AllParamSaveType]] = {}
    for k, v in asdict(params).items():
        v = cast(AllParamType | dict[str, AllParamType], v)
        if isinstance(v, dict):
            res[k] = params2Save(cast(DataclassInstance, v))
        else:
            res[k] = v.toSave()
    return res
