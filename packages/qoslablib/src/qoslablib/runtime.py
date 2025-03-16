from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import functools
from threading import Lock

from .extensions.saver import SqlSaverManagerABC
from .extensions.chart import ChartManagerABC

from . import params


class ManagerABC(SqlSaverManagerABC, ChartManagerABC):
    @abstractmethod
    def initializeExtensions(self, experiment_id: str):
        raise NotImplementedError


@dataclass
class ExperimentABC(ABC):
    # Instance shall initiate params in __init__() function
    params: params.Params

    class LoopCount:
        INFINITE = -1

        @classmethod
        def FINITE(loop: int):
            return loop

    def __init__(self):
        pass

    # The __init__ of the exact experiment should look sth like this

    # def __init__(self, holder: ManagerABC):
    #     # Call super for forward compatability
    #     super()__init__(self)

    #     # List of params with default values
    #     # This list will NOT be the final list of parameter used in the experiment
    #     # Instead, this list is passed to the webapp to start with. The complete list
    #     # with updated values will be passed during "initialization" phase (initialization function)
    #     self.params = {
    #         "power": qoslablib.params.int_param(-3)
    #         "other param": ...
    #     }

    #     # Create chart objects
    #     self.chart = holder.createChart(XYPlot, kwargs={"title": "title of the plot"})

    #     # Create data objects to save data
    #     # Refer to the actual sqlsaver for the parameters needed
    #     self.data = holder.createSqlSaver(XYSqlSaver, kwargs={"title": "some title"})

    @abstractmethod
    def initialize(self) -> int:
        # # params list would already be the most update
        # # You may use the params directly as follows
        # self.params

        # # instantiate variables that needes to be used during the experiment
        # self.mv =  Array(params.mv_range_min,params.mv_range_max) # Or sth with np
        # self.lockin = self.params.lockin

        # This function should interact with equipment and do stuff that shall only run once each experiment
        # Only use this function to perform initialization of equipment

        # # This function shall return the number of loops, it needs to be integer / -1 for infinity

        # # e.g.
        # <cls>.Loop.FOR(30)
        # <cls>.Loop.FOREVER

        raise NotImplementedError

    @abstractmethod
    def loop(self, index: int):
        # This function should take in the index and perform one loop of the experiment.
        # Something like:
        # mv = self.mv[index]
        # self.sigen.frequency = mv
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        # This function should do any clean up if needed
        # However, this function is not a must to be implemented
        pass


# This is a decorator to ensure thread safe access of equipment
# All equipment functions shall use this decorator
# Example refer to the EquipmentABC below
def EquipmentTLock(func):
    @functools.wraps(func)
    def wrapper(self: EquipmentABC, *args, **kwargs):
        with self._qoslab_equipment_thread_lock:
            return func(self, *args, **kwargs)

    return wrapper


@dataclass
class EquipmentABC(ABC):
    # Instance shall initiate params in __init__() function
    params: params.Params

    # # All equipment subclass shall call __init__ function FIRST in their __init__ functions

    # # e.g.

    # def __init__(self):
    #     super().__init__()
    #     self.params = {
    #         # Same as experiment, refer to experiment for example,
    #         # refer to params page for documentation of specifying params
    #     }
