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

from abc import ABC
from typing import Any, Literal, TypedDict
from .equipment import EquipmentABC


class ParamBase(ABC):
    def __init__(self, required: bool):
        self.required = required


class SelectStrParam(ParamBase):
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

    def __init__(
        self, options: list[str], value: str | None = None, required: bool = False
    ):
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
        super().__init__(required)

    class DictType(TypedDict):
        type: Literal["select.str"]
        options: list[str]
        value: str
        required: bool

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(data["options"], data["value"], data["required"])

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "options": self._options,
            "value": self.value,
            "required": self.required,
        }

    def toSave(self):
        return {"value": self.value}


class SelectIntParam(ParamBase):
    """Single select of int type. Detail refer to SelectStrParam class"""

    type: Literal["select.int"] = "select.int"

    def __init__(
        self, options: list[int], value: int | None = None, required: bool = False
    ):
        self._options = options
        self.value = options[0] if value is None else value
        super().__init__(required)

    class DictType(TypedDict):
        type: Literal["select.int"]
        options: list[int]
        value: int
        required: bool

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(data["options"], data["value"], data["required"])

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "options": self._options,
            "value": self.value,
            "required": self.required,
        }

    def toSave(self):
        return {"value": self.value}


class SelectFloatParam(ParamBase):
    """Single select of float type. Detail refer to SelectStrParam class"""

    type: Literal["select.float"] = "select.float"

    def __init__(
        self, options: list[float], value: float | None = None, required: bool = False
    ):
        self._options = options
        self.value = options[0] if value is None else value
        super().__init__(required)

    class DictType(TypedDict):
        type: Literal["select.float"]
        options: list[float]
        value: float
        required: bool

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(data["options"], data["value"], data["required"])

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "options": self._options,
            "value": self.value,
            "required": self.required,
        }

    def toSave(self):
        return {"value": self.value}


class IntParam(ParamBase):
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

    def __init__(self, default: int = 0, suffix: str = "", required: bool = False):
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
        super().__init__(required)

    class DictType(TypedDict):
        type: Literal["int"]
        suffix: str
        value: int
        required: bool

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(data["value"], data["suffix"], data["required"])

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "suffix": self.suffix,
            "value": self.value,
            "required": self.required,
        }

    def toSave(self) -> dict[str, Any]:
        return {"value": self.value, "suffix": self.suffix}


class FloatParam(ParamBase):
    """IntParam but of float type. Detail refer to IntParam class

    Default value if none is given is 0.0
    """

    type: Literal["float"] = "float"

    def __init__(self, default: float = 0.0, suffix: str = "", required: bool = False):
        self.value = default
        self.suffix = suffix
        super().__init__(required)

    class DictType(TypedDict):
        type: Literal["float"]
        suffix: str
        value: float
        required: bool

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(data["value"], data["suffix"], data["required"])

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "suffix": self.suffix,
            "value": self.value,
            "required": self.required,
        }

    def toSave(self) -> dict[str, Any]:
        return {"value": self.value, "suffix": self.suffix}


class StrParam(ParamBase):
    """
    IntParam but of str type, without suffix. Detail refer to IntParam class.
    Default value if not given is empty string.
    """

    type: Literal["str"] = "str"

    def __init__(self, default: str = "", required: bool = False):
        self.value = default
        super().__init__(required)

    class DictType(TypedDict):
        type: Literal["str"]
        value: str
        required: bool

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(data["value"], data["required"])

    def toDict(self) -> DictType:
        return {"type": self.type, "value": self.value, "required": self.required}

    def toSave(self):
        return {"value": self.value}


class BoolParam(ParamBase):
    """
    IntParam but of bool type, without suffix. Detail refer to IntParam class.
    Default value if not given is empty string.
    """

    type: Literal["bool"] = "bool"

    def __init__(self, default: bool = False, required: bool = False):
        self.value = default
        super().__init__(required)

    class DictType(TypedDict):
        type: Literal["bool"]
        value: bool
        required: bool

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(data["value"], data["required"])

    def toDict(self) -> DictType:
        return {"type": self.type, "value": self.value, "required": self.required}

    def toSave(self):
        return {"value": self.value}


class InstanceEquipmentParam[T: EquipmentABC](ParamBase):
    """
    param type with instance implementing EquipmentProxy type

    Examples of utilizing the param please refer to examples

    Attributes
    ----------
    instance : EquipmentProxy[T]
        The wrapper class of the driver that implements the protocol
    """

    type: Literal["instance.equipment"] = "instance.equipment"

    def __init__(self, name: str | None = None, required: bool = False):
        self.name = name
        self.instance: T | None = None
        super().__init__(required)

    class DictType(TypedDict):
        type: Literal["instance.equipment"]
        name: str | None
        required: bool

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "name": self.name if self.name else None,
            "required": self.required,
        }

    @classmethod
    def fromDict(cls, data: DictType):
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")
        return cls(data["name"], data["required"])

    def toSave(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "params": cnoc_params2Dict(self.instance.params)  # type: ignore
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

#     type = "instance.experiment"

#     def __init__(self, name: str | None = None):
#         self.name = name
#         self.instance: T | None = None

#     def toDict(self):
#         return {
#             "type": self.type,
#             "name": self.name,
#         }

#     @classmethod
#     def fromDict(cls, data: dict):
#         if data["type"] != cls.type:
#             raise ValueError(f"Invalid type {data['type']} for {cls.type}")
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
    type: Literal["composite"] = "composite"

    def __init__(self, children: T):
        self.children = children

    class DictType(TypedDict):
        type: Literal["composite"]
        children: T

    def toDict(self) -> DictType:
        return {
            "type": self.type,
            "children": {k: v.toDict() for k, v in self.children.items()},  # type: ignore
        }

    @classmethod
    def fromDict(cls, data: DictType):  # type: ignore
        if data["type"] != cls.type:
            raise ValueError(f"Invalid type {data['type']} for {cls.type}")

        children: Params = {}  # type: ignore
        for k, v in data["children"].items():  # type: ignore
            for tp in _param_type_arr:  # type: ignore
                if v["type"] == tp.type:  # type: ignore
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


def cnoc_params2Dict(params: Params) -> dict[str, Any]:
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
        if v["type"] == CompositeParam.type:  # type: ignore
            params[k] = CompositeParam.fromDict(v)  # type: ignore
            continue

        for tp in _param_type_arr:  # type: ignore
            if v["type"] == tp.type:  # type: ignore
                params[k] = tp.fromDict(v)  # type: ignore
                break

    return params


def cnoc_params2Save(params: Params) -> dict[str, Any]:
    return {k: v.toSave() for k, v in params.items()}
