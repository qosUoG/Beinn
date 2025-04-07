from abc import ABC, abstractmethod
from dataclasses import dataclass
import dataclasses
from typing import Any, Literal, override
from pydantic import BaseModel

from packages.qoslabapp.lib.utils.result import ok


class QosParam[T: BaseModel](ABC):
    @abstractmethod
    def toBaseModel(self) -> T:
        # This function should return a BaseModel
        raise NotImplementedError

    @abstractmethod
    def getValue(self) -> str:
        raise NotImplementedError


@dataclass
class SelectStrParam(QosParam):
    type: Literal["select.str"]
    options: list[str]
    value: str

    class PydanticBaseModel(BaseModel):
        type: Literal["select.str"]
        options: list[str]
        value: str

        def toParam(self):
            return SelectStrParam(options=self.options, value=self.value)

    def __init__(self, options: list[str], value: str | None = None):
        self.type = "select.str"
        self.options = options
        if value is None:
            self.value = options[0]
        else:
            self.value = value

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(
            type=self.type, options=self.options, value=self.value
        )

    @override
    def getValue(self):
        return self.value


@dataclass
class SelectIntParam(QosParam):
    type: Literal["select.int"]
    options: list[int]
    value: int

    class PydanticBaseModel(BaseModel):
        type: Literal["select.int"]
        options: list[int]
        value: int

        def toParam(self):
            return SelectIntParam(options=self.options, value=self.value)

    def __init__(self, options: list[int], value: int | None = None):
        self.type = "select.int"
        self.options = options
        if value is None:
            self.value = options[0]
        else:
            self.value = value

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(
            type=self.type, options=self.options, value=self.value
        )

    @override
    def getValue(self):
        return f"{self.value}"


@dataclass
class SelectFloatParam:
    type: Literal["select.float"]
    options: list[float]
    value: int

    class PydanticBaseModel(BaseModel):
        type: Literal["select.float"]
        options: list[float]
        value: float

        def toParam(self):
            return SelectFloatParam(options=self.options, value=self.value)

    def __init__(self, options: list[float], value: float | None = None):
        self.type = "select.float"
        self.options = options
        if value is None:
            self.value = options[0]
        else:
            self.value = value

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(
            type=self.type, options=self.options, value=self.value
        )

    @override
    def getValue(self):
        return f"{self.value}"


@dataclass
class IntParam:
    type: Literal["int"]
    suffix: str
    value: int

    class PydanticBaseModel(BaseModel):
        type: Literal["int"]
        suffix: str
        value: int

        def toParam(self):
            return IntParam(default=self.value, suffix=self.suffix)

    def __init__(self, default: int = 0, suffix: str = ""):
        self.type = "int"
        self.suffix = suffix
        self.value = default

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(
            type=self.type, suffix=self.suffix, value=self.value
        )

    @override
    def getValue(self):
        return f"{self.value} {self.suffix}"


@dataclass
class FloatParam:
    type: Literal["float"]
    suffix: str
    value: float

    class PydanticBaseModel(BaseModel):
        type: Literal["float"]
        suffix: str
        value: float

        def toParam(self):
            return FloatParam(default=self.value, suffix=self.suffix)

    def __init__(self, default: float = 0, suffix: str = ""):
        self.type = "float"
        self.suffix = suffix
        self.value = default

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(
            type=self.type, suffix=self.suffix, value=self.value
        )

    @override
    def getValue(self):
        return f"{self.value} {self.suffix}"


@dataclass
class StrParam:
    type: Literal["str"]
    value: str

    class PydanticBaseModel(BaseModel):
        type: Literal["str"]
        value: str

        def toParam(self):
            return StrParam(default=self.value)

    def __init__(self, default: str = ""):
        self.type = "str"
        self.value = default

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(type=self.type, value=self.value)

    @override
    def getValue(self):
        return self.value


@dataclass
class BoolParam:
    type: Literal["bool"]
    value: bool

    class PydanticBaseModel(BaseModel):
        type: Literal["bool"]
        value: bool

        def toParam(self):
            return BoolParam(default=self.value)

    def __init__(self, default: bool = 0):
        self.type = "bool"
        self.value = default

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(type=self.type, value=self.value)

    @override
    def getValue(self):
        return f"{self.value}"


@dataclass
class InstanceEquipmentParam[T]:
    type: Literal["instance.equipment"]
    instance_id: str | None
    instance: T | None

    class PydanticBaseModel(BaseModel):
        type: Literal["instance.equipment"]
        instance_id: str | None

        def toParam(self):
            return InstanceEquipmentParam(instance_id=self.instance_id)

    def __init__(self, instance_id=None):
        self.type = "instance.equipment"
        self.instance_id = instance_id
        self.instance = None

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(type=self.type, instance_id=self.instance_id)

    @override
    def getValue(self):
        return f"{self.instance_id}"


@dataclass
class InstanceExperimentParam[T]:
    type: Literal["instance.experiment"]
    instance_id: str | None
    instance: T | None

    class PydanticBaseModel(BaseModel):
        type: Literal["instance.experiment"]
        instance_id: str | None

        def toParam(self):
            return InstanceExperimentParam(instance_id=self.instance_id)

    def __init__(self, instance_id=None):
        self.type = "instance.experiment"
        self.instance_id = instance_id
        self.instance = None

    @override
    def toBaseModel(self) -> PydanticBaseModel:
        return self.PydanticBaseModel(type=self.type, instance_id=self.instance_id)

    @override
    def getValue(self):
        return f"{self.instance_id}"


type AllParamTypes = (
    SelectStrParam
    | SelectFloatParam
    | SelectIntParam
    | IntParam
    | FloatParam
    | StrParam
    | BoolParam
    # | CompositeParam
    | InstanceEquipmentParam
    | InstanceExperimentParam
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


def Params2ParamModels(params: Params):
    res: ParamModels = {}
    for [name, param] in params.items():
        res[name] = param.toBaseModel()

    return res


type ParamModels = dict[str, AllParamModelTypes]


def ParamModels2Params(param_models: ParamModels):
    res: Params = {}
    for [name, param_model] in param_models.items():
        res[name] = param_model.toParam()

    return res


def ExperimentParamsToBackup(experiment_id: str, params: Params):
    res: dict[str, dict[str, str]] = {"experiment_id": experiment_id}

    def parseParams(id: str, _params: Params | None):
        if id in res:
            return

        res[id] = {}

        for [name, param] in _params.items():
            res[experiment_id][name] = param.getValue()

        # If the param is an instance, recursively parse the params as well
        if param.type == "instance.equipment" or param.type == "instance.experiment":
            if param.instance is not None:
                parseParams(param.instance_id, param.instance.params)

    parseParams(experiment_id, params)

    return res


# class CompositeParam:
#     type: Literal["composite"]
#     children: Params
