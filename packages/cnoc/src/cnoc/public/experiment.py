"""Base Class of Experiment, Experiment Manger

For examples of defining experiment class (scripts), please refer to examples in
example/examplelib.

    * Experiment - Base class of all experiment scripts
        Users shall define experiment scripts by using ExperimentABC as the base class.

"""

from abc import ABC, abstractmethod
from typing import Any, Callable

from .equipment import EquipmentABC
from .manager import Manager
from _typeshed import DataclassInstance


class ExperimentABC(ABC):
    """
    Base class of all experiment scripts

    Attributes
    ----------
    params : .params.Params
        a dictionary of parameters accessible by the experiment script

    """

    def setParams(
        self,
        params: dict[str, Any],
        equipments: dict[str, EquipmentABC[Any]],
        ParamsCls: type[DataclassInstance],
    ):
        from ._params import dict2Params

        self.params: DataclassInstance = dict2Params(params, equipments, ParamsCls)

    @abstractmethod
    def start(self, manager: Manager) -> None:
        raise NotImplementedError

    @abstractmethod
    def loop(self, index: int, shouldStop: Callable[[], bool]) -> None:
        raise NotImplementedError

    @abstractmethod
    def cleanup(self) -> None:
        raise NotImplementedError
