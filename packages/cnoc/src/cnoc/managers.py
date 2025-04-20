"""
Managers used by initialize of experiment script

    * ChartManagerABC - Base class of chart manager. Provide method to create chart instance.

    * ExperimentmanagerABC - Base class of manager received as parameter in initialize method
        contains the suggetTotalIterations method for the user to suggest the total number
        of iterations and display in frontend.

        The manager class implements all *managerABC of the framework. To look at the final
        ManagerABC, refer to runtime.py module.
"""

from abc import ABC, abstractmethod
from typing import Any
from .extensions.chart import _ChartABC
from .extensions.saver import _SaverABC


class ExperimentManagerABC(ABC):
    """
    ManagerABC of Experiment

    Methods
    -------
    suggestTotalIterations(total_iterations: int)
        suggest a total number of iterations loop is going to take
    """

    @abstractmethod
    def suggestTotalIterations(self, total_iterations: int):
        raise NotImplementedError


class ChartManagerABC(ABC):
    @abstractmethod
    def createChart(cls, chartT: type[_ChartABC], kwargs: Any) -> _ChartABC:
        """Returns a handle to the chart class, which shall have a plot function to be called in loop"""
        # This method returns a plot object
        raise NotImplementedError


class SaverManagerABC(ABC):
    # The holder shall manage the database connection, and provide a method that would be consumed by the SaverABC method

    @abstractmethod
    def createSaver[T: _SaverABC](cls, sql_saverT: type[T], kwargs: Any) -> T:
        """Returns a handle to the chart class, which shall have a save function to be called in loop"""
        raise NotImplementedError


class ManagerABC(SaverManagerABC, ChartManagerABC, ExperimentManagerABC):
    pass
