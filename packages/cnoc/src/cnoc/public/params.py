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

from abc import ABC, abstractmethod
from pickle import FALSE
from typing import Literal, override
from .experiment import ExperimentABC
from pydantic import BaseModel
from .equipment import EquipmentABC, EquipmentProxy


class _QosParam[T: BaseModel](ABC):
    @abstractmethod
    def toBaseModel(self) -> T:
        # This function should return a BaseModel
        raise NotImplementedError

    @abstractmethod
    def getValue(self) -> str:
        raise NotImplementedError


class SelectStrParam(_QosParam):
    """
    Singleselect param with value of type str

    Attributes
    ----------
    options : list[str]
        list of selectable options
    value : str
        the selected option
    """

    class PydanticBaseModel(BaseModel):
        type: Literal["select.str"]
        options: list[str]
        value: str

        def toParam(self):
            return SelectStrParam(options=self.options, value=self.value)

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
        self._type: Literal["select.str"] = "select.str"
        self.options = options
        if value is None:
            self.value = options[0]
        else:
            self.value = value

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(
            type=self._type, options=self.options, value=self.value
        )

    @override
    def getValue(self):
        return self.value


class SelectIntParam(_QosParam):
    """Singleselect of int type. Detail refer to SelectStrParam class"""

    class PydanticBaseModel(BaseModel):
        type: Literal["select.int"]
        options: list[int]
        value: int

        def toParam(self):
            return SelectIntParam(options=self.options, value=self.value)

    def __init__(self, options: list[int], value: int | None = None):
        self._type: Literal["select.int"] = "select.int"
        self.options = options
        if value is None:
            self.value = options[0]
        else:
            self.value = value

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(
            type=self._type, options=self.options, value=self.value
        )

    @override
    def getValue(self):
        return f"{self.value}"


class SelectFloatParam(_QosParam):
    """Singleselect of float type. Detail refer to SelectStrParam class"""

    class PydanticBaseModel(BaseModel):
        type: Literal["select.float"]
        options: list[float]
        value: float

        def toParam(self):
            return SelectFloatParam(options=self.options, value=self.value)

    def __init__(self, options: list[float], value: float | None = None):
        self._type: Literal["select.float"] = "select.float"
        self.options = options
        if value is None:
            self.value = options[0]
        else:
            self.value = value

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(
            type=self._type, options=self.options, value=self.value
        )

    @override
    def getValue(self):
        return f"{self.value}"


class IntParam(_QosParam):
    """
    param with value of type int

    Attributes
    ----------
    value : int
        the underlying value
    suffix : str
        suffix of the parameter displayed on frontend
    """

    class PydanticBaseModel(BaseModel):
        type: Literal["int"]
        suffix: str
        value: int

        def toParam(self):
            return IntParam(default=self.value, suffix=self.suffix)

    def __init__(self, default: int = 0, suffix: str = ""):
        """
        Parameters
        ----------
        default : int , optional
            default value of the param. If none is given, it would be assiged
            as 0

        suffix: str , optional
            suffix shown as hint on the frontend
        """
        self._type: Literal["int"] = "int"
        self.suffix = suffix
        self.value = default

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(
            type=self._type, suffix=self.suffix, value=self.value
        )

    @override
    def getValue(self):
        return f"{self.value} {self.suffix}"


class FloatParam(_QosParam):
    """IntParam but of float type. Detail refer to IntParam class

    Default value if none is given is 0.0
    """

    class PydanticBaseModel(BaseModel):
        type: Literal["float"]
        suffix: str
        value: float

        def toParam(self):
            return FloatParam(default=self.value, suffix=self.suffix)

    def __init__(self, default: float = 0.0, suffix: str = ""):
        self._type: Literal["float"] = "float"
        self.suffix = suffix
        self.value = default

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(
            type=self._type, suffix=self.suffix, value=self.value
        )

    @override
    def getValue(self):
        return f"{self.value} {self.suffix}"


class StrParam(_QosParam):
    """StrParam but of str type. Detail refer to IntParam class

    Do note that suffix is not provided in this param type

    Default value if not given is ""
    """

    class PydanticBaseModel(BaseModel):
        type: Literal["str"]
        value: str

        def toParam(self):
            return StrParam(default=self.value)

    def __init__(self, default: str = ""):
        self._type: Literal["str"] = "str"
        self.value = default

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(type=self._type, value=self.value)

    @override
    def getValue(self):
        return self.value


class BoolParam(_QosParam):
    """StrParam but of str type. Detail refer to IntParam class

    Do note that suffix is not provided in this param type

    Default value if not given is False
    """

    class PydanticBaseModel(BaseModel):
        type: Literal["bool"]
        value: bool

        def toParam(self):
            return BoolParam(default=self.value)

    def __init__(self, default: bool = FALSE):
        self._type: Literal["bool"] = "bool"
        self.value = default

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(type=self._type, value=self.value)

    @override
    def getValue(self):
        return f"{self.value}"


class InstanceEquipmentParam[T: EquipmentABC](_QosParam):
    """
    param type with instance implementing EquipmentProxy type

    Examples of utilizing the param please refer to examples

    Attributes
    ----------
    instance : EquipmentProxy[T]
        The wrapper class of the driver that implements the protocol
    """

    class PydanticBaseModel(BaseModel):
        type: Literal["instance.equipment"]
        instance_id: str | None

        def toParam(self):
            return InstanceEquipmentParam[T](self.instance_id)

    def __init__(self, instance_id: str | None = None):
        self._type: Literal["instance.equipment"] = "instance.equipment"
        self._instance_id = instance_id
        self.instance: EquipmentProxy[T] | None = None

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(type=self._type, instance_id=self._instance_id)

    @override
    def getValue(self):
        return f"{self._instance_id}"


class InstanceExperimentParam[T: ExperimentABC](_QosParam):
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

    class PydanticBaseModel(BaseModel):
        type: Literal["instance.experiment"]
        instance_id: str | None

        def toParam(self):
            return InstanceExperimentParam[T](self.instance_id)

    def __init__(self, instance_id: str | None = None):
        self._type: Literal["instance.experiment"] = "instance.experiment"
        self._instance_id = instance_id
        self.instance: T | None = None

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(type=self._type, instance_id=self._instance_id)

    @override
    def getValue(self):
        return f"{self._instance_id}"


type AllParamTypes = (
    SelectStrParam
    | SelectFloatParam
    | SelectIntParam
    | IntParam
    | FloatParam
    | StrParam
    | BoolParam
    # | CompositeParam
    | InstanceEquipmentParam[EquipmentABC]
    | InstanceExperimentParam[ExperimentABC]
)

type AllParamModelTypes = (
    SelectStrParam.PydanticBaseModel
    | SelectFloatParam.PydanticBaseModel
    | SelectIntParam.PydanticBaseModel
    | IntParam.PydanticBaseModel
    | FloatParam.PydanticBaseModel
    | StrParam.PydanticBaseModel
    | BoolParam.PydanticBaseModel
    # | CompositeParam.PydanticBaseModel
    | InstanceEquipmentParam.PydanticBaseModel
    | InstanceExperimentParam.PydanticBaseModel
)

type Params = dict[str, AllParamTypes]


# class CompositeParam:
#     _type: Literal["composite"]
#     children: Params
