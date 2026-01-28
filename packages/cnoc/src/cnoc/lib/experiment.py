"""Base Class of Experiment, Experiment Manger

For examples of defining experiment class (scripts), please refer to examples in
example/examplelib.

    * Experiment - Base class of all experiment scripts
        Users shall define experiment scripts by using ExperimentABC as the base class.

"""

from abc import ABC, abstractmethod
from typing import Any, Callable, cast

from .equipment import EquipmentABC
from .manager import Manager
from ._utils import DataclassInstance


class ExperimentABC[T: DataclassInstance](ABC):
    """
    Base class of all experiment scripts

    Attributes
    ----------
    params : .params.Params
        a dictionary of parameters accessible by the experiment script

    """

    def __init__(self):
        self.params: T

    def setParams(
        self,
        params: dict[str, Any],
        equipments: dict[str, EquipmentABC[Any]],
        ParamsCls: type[DataclassInstance],
    ):
        from ._params import dict2Params

        self.params = cast(T, dict2Params(params, equipments, ParamsCls))

    @abstractmethod
    def start(self, manager: Manager) -> None:
        raise NotImplementedError

    # In another thread
    @abstractmethod
    def loop(self, index: int, shouldStop: Callable[[], bool]) -> None:
        raise NotImplementedError

    @abstractmethod
    def cleanup(self) -> None:
        raise NotImplementedError
