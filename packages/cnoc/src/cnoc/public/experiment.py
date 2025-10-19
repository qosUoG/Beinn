"""Base Class of Experiment, Experiment Manger

For examples of defining experiment class (scripts), please refer to examples in
example/examplelib.

    * Experiment - Base class of all experiment scripts
        Users shall define experiment scripts by using ExperimentABC as the base class.

"""

from abc import ABC, abstractmethod
from .manager import Manager


class ExperimentABC(ABC):
    """
    Base class of all experiment scripts

    Attributes
    ----------
    params : .params.Params
        a dictionary of parameters accessible by the experiment script

    """

    @abstractmethod
    def start(self, cnoc: Manager) -> None:
        raise NotImplementedError

    @abstractmethod
    def loop(self, index: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def cleanup(self) -> None:
        raise NotImplementedError
