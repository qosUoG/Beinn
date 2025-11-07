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

from typing import Any, Generic, Literal, Type, TypedDict, cast, TypeVar
from .equipment import EquipmentABC


class SelectStrParam:
    """
    Single select param with value of type str

    Attributes
    ----------
    options : list[str]
        list of selectable options
    value : str
        the selected option
    """

    type: Literal["select.str"] = "select.str"

    def __init__(self, options: list[str], value: str | None = None):
        """
        Parameters
        ----------
        options : list[str]
            available options to select

        value : str , optional
            default value of the param. If none is given, the first option
            would be used
        """
        self._options = options
        self.value = value if value is not None and value in options else options[0]

    class DictType(TypedDict):
        type: Literal["select.str"]
        options: list[str]
        value: str

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(data["options"], data["value"])

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "options": self._options,
            "value": self.value,
        }

    def toSave(self):
        return {"value": self.value}


class SelectIntParam:
    """Single select of int type. Detail refer to SelectStrParam class"""

    type: Literal["select.int"] = "select.int"

    def __init__(self, options: list[int], value: int | None = None):
        self._options = options
        self.value = value if value is not None and value in options else options[0]

    class DictType(TypedDict):
        type: Literal["select.int"]
        options: list[int]
        value: int

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(
            data["options"],
            data["value"],
        )

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "options": self._options,
            "value": self.value,
        }

    def toSave(self):
        return {"value": self.value}


class SelectFloatParam:
    """Single select of float type. Detail refer to SelectStrParam class"""

    type: Literal["select.float"] = "select.float"

    def __init__(self, options: list[float], value: float | None = None):
        self._options = options
        self.value = value if value is not None and value in options else options[0]

    class DictType(TypedDict):
        type: Literal["select.float"]
        options: list[float]
        value: float

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(
            data["options"],
            data["value"],
        )

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "options": self._options,
            "value": self.value,
        }

    def toSave(self):
        return {"value": self.value}


class IntParam:
    """
    param with value of type int

    Attributes
    ----------
    value : int
        the underlying value
    suffix : str
        suffix of the parameter displayed on frontend
    """

    type: Literal["int"] = "int"

    def __init__(self, default: int = 0, suffix: str = ""):
        """
        Parameters
        ----------
        default : int , optional
            default value of the param. If none is given, it would be assigned
            as 0

        suffix: str , optional
            suffix shown as hint on the frontend
        """
        self.value = default
        self.suffix = suffix

    class DictType(TypedDict):
        type: Literal["int"]
        suffix: str
        value: int

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(
            data["value"],
            data["suffix"],
        )

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "suffix": self.suffix,
            "value": self.value,
        }

    def toSave(self) -> dict[str, Any]:
        return {"value": self.value, "suffix": self.suffix}


class FloatParam:
    """IntParam but of float type. Detail refer to IntParam class

    Default value if none is given is 0.0
    """

    type: Literal["float"] = "float"

    def __init__(self, default: float = 0.0, suffix: str = ""):
        self.value = default
        self.suffix = suffix

    class DictType(TypedDict):
        type: Literal["float"]
        suffix: str
        value: float

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(
            data["value"],
            data["suffix"],
        )

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "suffix": self.suffix,
            "value": self.value,
        }

    def toSave(self) -> dict[str, Any]:
        return {"value": self.value, "suffix": self.suffix}


class StrParam:
    """
    IntParam but of str type, without suffix. Detail refer to IntParam class.
    Default value if not given is empty string.
    """

    type: Literal["str"] = "str"

    def __init__(self, default: str = ""):
        self.value = default

    class DictType(TypedDict):
        type: Literal["str"]
        value: str

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(
            data["value"],
        )

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "value": self.value,
        }

    def toSave(self):
        return {"value": self.value}


class BoolParam:
    """
    IntParam but of bool type, without suffix. Detail refer to IntParam class.
    Default value if not given is empty string.
    """

    type: Literal["bool"] = "bool"

    def __init__(self, default: bool = False):
        self.value = default

    class DictType(TypedDict):
        type: Literal["bool"]
        value: bool

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(
            data["value"],
        )

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "value": self.value,
        }

    def toSave(self):
        return {"value": self.value}


_GenericEquipment = TypeVar("_GenericEquipment", bound=EquipmentABC)


class InstanceEquipmentParam(Generic[_GenericEquipment]):
    """
    param type with instance implementing EquipmentProxy type

    Examples of utilizing the param please refer to examples

    Attributes
    ----------
    instance : EquipmentProxy[T]
        The wrapper class of the driver that implements the protocol
    """

    type: Literal["instance.equipment"] = "instance.equipment"

    def __init__(self):
        self.value: str | None = None
        self.instance: _GenericEquipment | None = None

        #

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
        param = cls()
        if data["value"] is not None:
            if data["value"] not in equipments:
                raise ValueError(f"Equipment {data['value']} not found.")
            param.value = data["value"]
            param.instance = cast(_GenericEquipment, equipments[data["value"]])

        return param

    def toSave(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "params": params2Dict(cast(Params, self.instance.params))  # type: ignore
            if self.instance
            else None,
        }


type _SimpleParamType = (
    SelectStrParam
    | SelectFloatParam
    | SelectIntParam
    | IntParam
    | FloatParam
    | StrParam
    | BoolParam
    | InstanceEquipmentParam[EquipmentABC]
)

type _SimpleParamDictType = (
    SelectStrParam.DictType
    | SelectFloatParam.DictType
    | SelectIntParam.DictType
    | IntParam.DictType
    | FloatParam.DictType
    | StrParam.DictType
    | BoolParam.DictType
    | InstanceEquipmentParam[EquipmentABC].DictType
)

Children = TypeVar("Children", bound=dict[str, _SimpleParamType])


_CompositeChildrenTypesType = TypedDict(
    "_CompositeChildrenTypesType",
    {
        "select.str": Type[SelectStrParam],
        "select.float": Type[SelectFloatParam],
        "select.int": Type[SelectIntParam],
        "int": Type[IntParam],
        "float": Type[FloatParam],
        "str": Type[StrParam],
        "bool": Type[BoolParam],
        "instance.equipment": Type[InstanceEquipmentParam[EquipmentABC]],
    },
)


_CompositeChildrenTypes: _CompositeChildrenTypesType = {
    "select.str": SelectStrParam,
    "select.float": SelectFloatParam,
    "select.int": SelectIntParam,
    "int": IntParam,
    "float": FloatParam,
    "str": StrParam,
    "bool": BoolParam,
    "instance.equipment": InstanceEquipmentParam[EquipmentABC],
}


class CompositeParam(Generic[Children]):
    type: Literal["composite"] = "composite"

    def __init__(self, children: Children):
        self.children = children

    class DictType(TypedDict):
        type: Literal["composite"]
        children: dict[str, _SimpleParamDictType]

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "children": {k: v.toDict() for k, v in self.children.items()},
        }

    @classmethod
    def fromDict(
        cls, data: DictType, equipments: dict[str, EquipmentABC]
    ) -> "CompositeParam[Children]":
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")

        children: Children = cast(Children, {})
        for k, v in data["children"].items():
            tp = _CompositeChildrenTypes[v["type"]]

            match tp.type:
                case "bool":
                    assert v["type"] == "bool"
                    children[k] = tp.fromDict(v)
                case "float":
                    assert v["type"] == "float"
                    children[k] = tp.fromDict(v)
                case "int":
                    assert v["type"] == "int"
                    children[k] = tp.fromDict(v)
                case "str":
                    assert v["type"] == "str"
                    children[k] = tp.fromDict(v)
                case "select.str":
                    assert v["type"] == "select.str"
                    children[k] = tp.fromDict(v)
                case "select.int":
                    assert v["type"] == "select.int"
                    children[k] = tp.fromDict(v)
                case "select.float":
                    assert v["type"] == "select.float"
                    children[k] = tp.fromDict(v)
                case "instance.equipment":
                    assert v["type"] == "instance.equipment"
                    children[k] = tp.fromDict(v, equipments)

        return CompositeParam[Children](children)

    def toSave(self):
        return {k: v.toSave() for k, v in self.children.items()}


type AllParamType = _SimpleParamType | CompositeParam[dict[str, _SimpleParamType]]
type Params = dict[str, AllParamType]

type AllParamDictType = (
    _SimpleParamDictType | CompositeParam[dict[str, _SimpleParamType]].DictType
)


_AllParamsTypesType = TypedDict(
    "_AllParamsTypesType",
    {
        "select.str": Type[SelectStrParam],
        "select.float": Type[SelectFloatParam],
        "select.int": Type[SelectIntParam],
        "int": Type[IntParam],
        "float": Type[FloatParam],
        "str": Type[StrParam],
        "bool": Type[BoolParam],
        "instance.equipment": Type[InstanceEquipmentParam[EquipmentABC]],
        "composite": Type[CompositeParam[dict[str, _SimpleParamType]]],
    },
)


_AllParamsTypes: _AllParamsTypesType = {
    "select.str": SelectStrParam,
    "select.float": SelectFloatParam,
    "select.int": SelectIntParam,
    "int": IntParam,
    "float": FloatParam,
    "str": StrParam,
    "bool": BoolParam,
    "instance.equipment": InstanceEquipmentParam[EquipmentABC],
    "composite": CompositeParam[dict[str, _SimpleParamType]],
}


def params2Dict(params: Params) -> dict[str, Any]:
    """
    Convert the params to a dictionary representation
    """
    return {k: v.toDict() for k, v in params.items()}


def dict2Params(
    data: dict[str, AllParamDictType], equipments: dict[str, EquipmentABC]
) -> Params:
    """
    Convert the dictionary representation back to Params
    However this function does not set the instance of the params,
    i.e. the instance must be set after all instances are loaded
    """
    params: Params = {}
    for k, v in data.items():
        tp = _AllParamsTypes[v["type"]]

        match tp.type:
            case "bool":
                assert v["type"] == "bool"
                params[k] = tp.fromDict(v)
            case "float":
                assert v["type"] == "float"
                params[k] = tp.fromDict(v)
            case "int":
                assert v["type"] == "int"
                params[k] = tp.fromDict(v)
            case "str":
                assert v["type"] == "str"
                params[k] = tp.fromDict(v)
            case "select.str":
                assert v["type"] == "select.str"
                params[k] = tp.fromDict(v)
            case "select.int":
                assert v["type"] == "select.int"
                params[k] = tp.fromDict(v)
            case "select.float":
                assert v["type"] == "select.float"
                params[k] = tp.fromDict(v)
            case "instance.equipment":
                assert v["type"] == "instance.equipment"
                params[k] = tp.fromDict(v, equipments)
            case "composite":
                assert v["type"] == "composite"
                params[k] = CompositeParam.fromDict(v, equipments)

    return params


def params2Save(params: Params) -> dict[str, Any]:
    return {k: v.toSave() for k, v in params.items()}
