import importlib
from types import ModuleType
from fastapi import WebSocket
from qoslablib.params import Params

from ..proxies.sql_saver import SqlWorker

from ..proxies.experiment import ExperimentProxy
from ..proxies.equipment import EquipmentProxy


class AppState:
    """Equipments Experiments shared code"""

    @classmethod
    def importModule(
        cls,
        list: list[ModuleType],
        module_str: str,
    ):
        module = importlib.import_module(module_str)
        if module in list:
            list.remove(module)
            module = importlib.reload(module)
        list.append(module)
        return module

    """
    Equipments 
    """

    _equipments_proxies: dict[str, EquipmentProxy] = {}
    _equipment_imported_modules: list[ModuleType] = []

    @classmethod
    def createEquipment(cls, id: str, module_str: str, ecls_str: str):
        module = cls.importModule(cls._equipment_imported_modules, module_str)
        cls._equipments_proxies[id] = EquipmentProxy(getattr(module, ecls_str))

    @classmethod
    def getEquipment(cls, id: str):
        return cls._equipments_proxies[id]

    @classmethod
    def getEquipmentParams(cls, id: str):
        return cls._equipments_proxies[id].params

    @classmethod
    def setEquipmentParams(cls, id: str, params: Params):
        cls._equipments_proxies[id].params = params

    @classmethod
    def removeEquipment(cls, id: str):
        if id in cls._equipments_proxies:
            del cls._equipments_proxies[id]

    """
    Experiments 
    """
    _experiment_proxies: dict[str, ExperimentProxy] = {}
    _experiment_imported_modules: list[ModuleType] = []

    @classmethod
    def createExperiment(cls, id: str, module_str: str, ecls_str: str):
        module = cls.importModule(cls._experiment_imported_modules, module_str)

        cls._experiment_proxies[id] = ExperimentProxy(
            id=id,
            experimentCls=getattr(module, ecls_str),
        )

    @classmethod
    def setExperimentParams(cls, id: str, params: Params):
        cls._experiment_proxies[id].params = params

    @classmethod
    def getExperimentParams(cls, id: str):
        return cls._experiment_proxies[id].params

    @classmethod
    def removeExperiment(cls, id: str):
        if id not in cls._experiment_proxies:
            return

        cls._experiment_proxies[id].cleanup()

        del cls._experiment_proxies[id]

    @classmethod
    def startExperiment(cls, id: str):
        cls._experiment_proxies[id].start()

    @classmethod
    def pauseExperiment_sync(cls, id: str):
        cls._experiment_proxies[id].pause_sync()

    @classmethod
    def continueExperiment(cls, id: str):
        cls._experiment_proxies[id].unpause()

    @classmethod
    def stopExperiment_sync(cls, id: str):
        cls._experiment_proxies[id].stop_async()

    @classmethod
    def subscribeExperimentMessage(cls, id: str, ws: WebSocket):
        return cls._experiment_proxies[id].subscribeMessage(ws)

    """Experiment Extensions"""

    @classmethod
    def subscribeChart(cls, id: str, title: str, ws: WebSocket):
        return cls._experiment_proxies[id].subscribeChart(title, ws)

    """App Life cycle"""

    @classmethod
    def start(cls):
        # Start the worker
        SqlWorker.start()

    @classmethod
    async def cleanup(cls):
        """This function is meant to be stopping gracefully. Timeout should be handled outside of this function"""

        # First stop async for each function
        for experiment_proxy in cls._experiment_proxies.values():
            experiment_proxy.stop_async()

        # Then wait until each experiment is actually stopped and do cleanup
        for experiment_proxy in cls._experiment_proxies.values():
            await experiment_proxy.forceStop()
            await experiment_proxy.waitUntil_stopped()

        # Stop all workers
        await SqlWorker.stop()
