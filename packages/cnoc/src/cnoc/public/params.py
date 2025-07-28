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

    * InstanceEquipmentParam - param type with value implementing EquipmentProxy type
    * InstanceExperimentParam - param type with value inheriting ExperimentABC type

"""

from abc import ABC
from .experiment import ExperimentABC
from .equipment import EquipmentABC, EquipmentProxy


class SingleSelectABC[T: str | int | float](ABC):
    """
    Base class for single select param type
    """

    _type: str

    def __init__(self, options: list[str], value: T | None = None):
        self._options = options
        self.value = options[0] if value is None else value

    # To and from json
    def toDict(self):
        return {"type": self._type, "options": self._options, "value": self.value}


class SelectStrParam(SingleSelectABC[str]):
    """
    Single select param with value of type str

    Attributes
    ----------
    options : list[str]
        list of selectable options
    value : str
        the selected option
    """

    _type = "select.str"

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
        super().__init__(options, value)

    @classmethod
    def fromDict(cls, data: dict):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["options"], data["value"])


class SelectIntParam(SingleSelectABC[int]):
    """Single select of int type. Detail refer to SelectStrParam class"""

    _type = "select.int"

    def __init__(self, options: list[int], value: int | None = None):
        super().__init__(options, value)

    @classmethod
    def fromDict(cls, data: dict):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["options"], data["value"])


class SelectFloatParam(SingleSelectABC[float]):
    """Single select of float type. Detail refer to SelectStrParam class"""

    _type = "select.float"

    def __init__(self, options: list[float], value: float | None = None):
        super().__init__(options, value)

    @classmethod
    def fromDict(cls, data: dict):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["options"], data["value"])


class NumberABC[T: int | float](ABC):
    """
    Base class for Number param type
    """

    _type: str

    def __init__(
        self,
        default: T,  # Default value is 0 for int and float
        suffix: str,
    ):
        self.value = default
        self.suffix = suffix

    # To and from json
    def toDict(self):
        return {"type": self._type, "suffix": self.suffix, "value": self.value}


class IntParam(NumberABC[int]):
    """
    param with value of type int

    Attributes
    ----------
    value : int
        the underlying value
    suffix : str
        suffix of the parameter displayed on frontend
    """

    _type = "int"

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
        super().__init__(default, suffix)

    @classmethod
    def fromDict(cls, data: dict):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["value"], data["suffix"])


class FloatParam(NumberABC[float]):
    """IntParam but of float type. Detail refer to IntParam class

    Default value if none is given is 0.0
    """

    _type = "float"

    def __init__(self, default: float = 0.0, suffix: str = ""):
        super().__init__(default, suffix)

    @classmethod
    def fromDict(cls, data: dict):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["value"], data["suffix"])


class PrimitiveABC[T: str | bool](ABC):
    """
    Base class for Number param type
    """

    _type: str

    def __init__(
        self,
        default: T,  # Default value is "" for str and False for bool
    ):
        self.value = default

    # To and from json
    def toDict(self):
        return {"type": self._type, "value": self.value}


class StrParam(PrimitiveABC[str]):
    """
    IntParam but of str type, without suffix. Detail refer to IntParam class.
    Default value if not given is empty string.
    """

    _type = "str"

    def __init__(self, default: str = ""):
        super().__init__(default)

    @classmethod
    def fromDict(cls, data: dict):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["value"])


class BoolParam(PrimitiveABC[bool]):
    """
    IntParam but of bool type, without suffix. Detail refer to IntParam class.
    Default value if not given is empty string.
    """

    _type = "bool"

    def __init__(self, default: bool = False):
        super().__init__(default)

    @classmethod
    def fromDict(cls, data: dict):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["value"])


class InstanceEquipmentParam[T: EquipmentABC]:
    """
    param type with instance implementing EquipmentProxy type

    Examples of utilizing the param please refer to examples

    Attributes
    ----------
    instance : EquipmentProxy[T]
        The wrapper class of the driver that implements the protocol
    """

    _type = "instance.equipment"

    def __init__(self, name: str | None = None):
        self._name = name
        self.instance: EquipmentProxy[T] | None = None

    def toDict(self):
        return {
            "type": self._type,
            "name": self._name,
        }

    @classmethod
    def fromDict(cls, data: dict):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["name"])


class InstanceExperimentParam[T: ExperimentABC]:
    """
    param type with instance inheriting ExperimentABC type

    NOTE THAT this param type is not being supported yet. This
    will be intended for playlist feature.

    Examples of utilizing the param please refer to examples

    Attributes
    ----------
    instance : [T : ExperimentABC]
        The wrapper class of the experiment that implements the protocol
    """

    _type = "instance.experiment"

    def __init__(self, name: str | None = None):
        self._name = name
        self.instance: EquipmentProxy[T] | None = None

    def toDict(self):
        return {
            "type": self._type,
            "name": self._name,
        }

    @classmethod
    def fromDict(cls, data: dict):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")
        return cls(data["name"])


type _SimpleParamType = (
    SelectStrParam
    | SelectFloatParam
    | SelectIntParam
    | IntParam
    | FloatParam
    | StrParam
    | BoolParam
    | InstanceEquipmentParam[EquipmentABC]
    | InstanceExperimentParam[ExperimentABC]
)


class CompositeParam:
    _type = "composite"

    def __init__(self, title: str, children: dict[str, _SimpleParamType]):
        self.title = title
        self.children = children

    def toDict(self):
        return {
            "type": self._type,
            "title": self.title,
            "children": {k: v.toDict() for k, v in self.children.items()},
        }

    @classmethod
    def fromDict(cls, data: dict):
        if data["type"] != cls._type:
            raise ValueError(f"Invalid type {data['type']} for {cls._type}")

        children: Params = {}
        for k, v in data.items():
            for tp in _param_type_arr:
                if v["type"] == tp._type:
                    children[k] = tp.fromDict(v)
                    break

        return CompositeParam(
            data["title"],
            children,
        )


type AllParamTypes = _SimpleParamType | CompositeParam
type Params = dict[str, AllParamTypes]


_param_type_arr: list[AllParamTypes] = [
    SelectStrParam,
    SelectIntParam,
    SelectFloatParam,
    IntParam,
    FloatParam,
    StrParam,
    BoolParam,
    InstanceEquipmentParam[EquipmentABC],
    InstanceExperimentParam[ExperimentABC],
    CompositeParam,
]


def param2Dict(params: Params) -> dict[str, dict]:
    """
    Convert the params to a dictionary representation
    """
    return {k: v.toDict() for k, v in params.items()}
