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

# from .experiment import ExperimentABC

from typing import Any, Literal, TypedDict
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

    _type: Literal["select.str"] = "select.str"

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
        self.value = options[0] if value is None else value

    class DictType(TypedDict):
        type: Literal["select.str"]
        options: list[str]
        value: str

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["options"], data["value"])

    def toDict(self) -> DictType:
        return {"type": self._type, "options": self._options, "value": self.value}

    def toSave(self):
        return {"value": self.value}


class SelectIntParam:
    """Single select of int type. Detail refer to SelectStrParam class"""

    _type: Literal["select.int"] = "select.int"

    def __init__(self, options: list[int], value: int | None = None):
        self._options = options
        self.value = options[0] if value is None else value

    class DictType(TypedDict):
        type: Literal["select.int"]
        options: list[int]
        value: int

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["options"], data["value"])

    def toDict(self) -> DictType:
        return {"type": self._type, "options": self._options, "value": self.value}

    def toSave(self):
        return {"value": self.value}


class SelectFloatParam:
    """Single select of float type. Detail refer to SelectStrParam class"""

    _type: Literal["select.float"] = "select.float"

    def __init__(self, options: list[float], value: float | None = None):
        self._options = options
        self.value = options[0] if value is None else value

    class DictType(TypedDict):
        type: Literal["select.float"]
        options: list[float]
        value: float

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["options"], data["value"])

    def toDict(self) -> DictType:
        return {"type": self._type, "options": self._options, "value": self.value}

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

    _type: Literal["int"] = "int"

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
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["value"], data["suffix"])

    def toDict(self) -> DictType:
        return {"type": self._type, "suffix": self.suffix, "value": self.value}

    def toSave(self) -> dict[str, Any]:
        return {"value": self.value, "suffix": self.suffix}


class FloatParam:
    """IntParam but of float type. Detail refer to IntParam class

    Default value if none is given is 0.0
    """

    _type: Literal["float"] = "float"

    def __init__(self, default: float = 0.0, suffix: str = ""):
        self.value = default
        self.suffix = suffix

    class DictType(TypedDict):
        type: Literal["float"]
        suffix: str
        value: float

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["value"], data["suffix"])

    def toDict(self) -> DictType:
        return {"type": self._type, "suffix": self.suffix, "value": self.value}

    def toSave(self) -> dict[str, Any]:
        return {"value": self.value, "suffix": self.suffix}


class StrParam:
    """
    IntParam but of str type, without suffix. Detail refer to IntParam class.
    Default value if not given is empty string.
    """

    _type: Literal["str"] = "str"

    def __init__(self, default: str = ""):
        self.value = default

    class DictType(TypedDict):
        type: Literal["str"]
        value: str

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["value"])

    def toDict(self) -> DictType:
        return {"type": self._type, "value": self.value}

    def toSave(self):
        return {"value": self.value}


class BoolParam:
    """
    IntParam but of bool type, without suffix. Detail refer to IntParam class.
    Default value if not given is empty string.
    """

    _type: Literal["bool"] = "bool"

    def __init__(self, default: bool = False):
        self.value = default

    class DictType(TypedDict):
        type: Literal["bool"]
        value: bool

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["value"])

    def toDict(self) -> DictType:
        return {"type": self._type, "value": self.value}

    def toSave(self):
        return {"value": self.value}


class InstanceEquipmentParam[T: EquipmentABC]:
    """
    param type with instance implementing EquipmentProxy type

    Examples of utilizing the param please refer to examples

    Attributes
    ----------
    instance : EquipmentProxy[T]
        The wrapper class of the driver that implements the protocol
    """

    _type: Literal["instance.equipment"] = "instance.equipment"

    def __init__(self, name: str | None = None):
        self.name = name
        self.instance: T | None = None

    class DictType(TypedDict):
        type: Literal["instance.equipment"]
        name: str

    def toDict(self) -> DictType:
        return {
            "type": self._type,
            "name": self.name if self.name else "",
        }

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["name"])

    def toSave(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "params": _cnoc_params2Dict(self.instance.params)  # type: ignore
            if self.instance
            else None,
        }


# class InstanceExperimentParam[T: ExperimentABC]:
#     """
#     param type with instance inheriting ExperimentABC type

#     NOTE THAT this param type is not being supported yet. This
#     will be intended for playlist feature.

#     Examples of utilizing the param please refer to examples

#     Attributes
#     ----------
#     instance : [T : ExperimentABC]
#         The wrapper class of the experiment that implements the protocol
#     """

#     _type = "instance.experiment"

#     def __init__(self, name: str | None = None):
#         self.name = name
#         self.instance: T | None = None

#     def toDict(self):
#         return {
#             "type": self._type,
#             "name": self.name,
#         }

#     @classmethod
#     def fromDict(cls, data: dict):
#         if data["type"] != cls._type:
#             raise ValueError(f"Invalid type {data['type']} for {cls._type}")
#         return cls(data["name"])


type _SimpleParamType = (
    SelectStrParam
    | SelectFloatParam
    | SelectIntParam
    | IntParam
    | FloatParam
    | StrParam
    | BoolParam
    | InstanceEquipmentParam[EquipmentABC]
    # | InstanceExperimentParam[ExperimentABC]
)


class CompositeParam[T]:
    _type: Literal["composite"] = "composite"

    def __init__(self, children: T):
        self.children = children

    class DictType(TypedDict):
        type: Literal["composite"]
        children: T

    def toDict(self) -> DictType:
        return {
            "type": self._type,
            "children": {k: v.toDict() for k, v in self.children.items()},  # type: ignore
        }

    @classmethod
    def fromDict(cls, data: DictType):  # type: ignore
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")

        children: Params = {}  # type: ignore
        for k, v in data["children"].items():  # type: ignore
            for tp in _param_type_arr:  # type: ignore
                if v["type"] == tp._type:  # type: ignore
                    children[k] = tp.fromDict(v)  # type: ignore
                    break

        return CompositeParam(children)  # type: ignore

    def toSave(self):  # type: ignore
        return {k: v.toSave() for k, v in self.children.items()}  # type: ignore


type AllParamTypes = _SimpleParamType | CompositeParam[_SimpleParamType]
type Params = dict[str, AllParamTypes]


_param_type_arr = [  # type: ignore
    SelectStrParam,
    SelectIntParam,
    SelectFloatParam,
    IntParam,
    FloatParam,
    StrParam,
    BoolParam,
    InstanceEquipmentParam[EquipmentABC],
    # InstanceExperimentParam[ExperimentABC],
    CompositeParam,
]


def _cnoc_params2Dict(params: Params) -> dict[str, Any]:
    """
    Convert the params to a dictionary representation
    """
    return {k: v.toDict() for k, v in params.items()}


def cnoc_dict2Params(data: dict[str, Any]) -> Params:
    """
    Convert the dictionary representation back to Params
    However this function does not set the instance of the params,
    i.e. the instance must be set after all instances are loaded
    """
    params: Params = {}
    for k, v in data.items():
        if v["type"] == CompositeParam._type:  # type: ignore
            params[k] = CompositeParam.fromDict(v)  # type: ignore
            continue

        for tp in _param_type_arr:  # type: ignore
            if v["type"] == tp._type:  # type: ignore
                params[k] = tp.fromDict(v)  # type: ignore
                break

    return params


def cnoc_params2Save(params: Params) -> dict[str, Any]:
    return {k: v.toSave() for k, v in params.items()}
