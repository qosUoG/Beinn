from abc import ABC, abstractmethod
from dataclasses import dataclass
import functools
from threading import Lock
from typing import ClassVar

from .saver import SqlSaverHolderABC
from .chart import ChartHolderABC

from .params import AllParamTypes


class AggregateHolderABC(SqlSaverHolderABC, ChartHolderABC):
    pass


@dataclass
class ExperimentABC(ABC):
    params: ClassVar[dict[str, AllParamTypes]]

    # Instance shall have this implemented
    params: dict[str, AllParamTypes]

    # The __init__ of the exact experiment should look sth like this

    # def __init__(self, params: dict[str, AllParamTypes], holder: AggregateHolderABC):

    #     # Save the params
    #     # Do all the checking here to make sure the params are within range
    #     # DO NOT interact with equipments here, any interaction with the equipments shall be done in the initialization stage
    #     self.params = params

    #     # instantiate variables that needes to be used during the experiment
    #     self.mv =  Array(params.mv_range_min,params.mv_range_max) # Or sth with np
    #     self.lockin = params.lockin

    #     # Create chart objects
    #     self.chart = holder.createChart(XYPlot, kwargs={"title": "title of the plot"})

    #     # Create data objects to save data
    #     # Refer to the actual sqlsaver for the parameters needed
    #     self.data = holder.createSqlSaver(XYSqlSaver, kwargs={"title": "some title"})

    @abstractmethod
    def initialize(self):
        # This function should interact with equipment and do stuff that shall only run once each experiment
        # Only use this function to perform initialization of equipment
        raise NotImplementedError

    @abstractmethod
    def loop(self, index: int):
        # This function should take in the index and perform one loop of the experiment.
        # Something like:
        # mv = self.mv[index]
        # self.sigen.frequency = mv
        raise NotImplementedError


@dataclass
class EquipmentABC(ABC):
    _qoslab_equipment_thread_lock: Lock

    def __init__(self):
        self._qoslab_equipment_thread_lock = Lock()

    def EquipmentTLock(func):
        @functools.wraps(func)
        def wrapper(self: EquipmentABC, *args, **kwargs):
            with self._qoslab_equipment_thread_lock:
                return func(self, *args, **kwargs)

        return wrapper
