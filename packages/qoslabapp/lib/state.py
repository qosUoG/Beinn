import asyncio
import importlib
from threading import Lock


from types import ModuleType
from typing import Any, override


from fastapi import WebSocket

from qoslablib.extensions.chart import ChartABC, ChartManagerABC
from qoslablib.extensions.saver import SqlSaverABC, SqlSaverManagerABC
from qoslablib.params import Params


from .workers.sqlite3 import SqlWorker

from .proxies.equipment import EquipmentProxy

from .proxies.experiment import ExperimentProxy

from .proxies.chart import ChartProxy
from .proxies.sql_saver import SqlSaverProxy


class AppState(ChartManagerABC, SqlSaverManagerABC):
    """
    Management of websocket connections
    """

    _ws: list[WebSocket] = []

    @classmethod
    def appendWs(cls, ws: WebSocket):
        cls._ws.append(ws)

    @classmethod
    async def disconnectAllWs(cls):
        for ws in cls._ws:
            await ws.close(code=1001)

    """
    Runtime management of Equipments
    """

    _equipments_proxies: dict[str, EquipmentProxy] = {}

    _equipment_imported_modules: list[ModuleType] = []

    @classmethod
    def createEquipment(cls, id: str, module_str: str, eCls: str):
        module = importlib.import_module(module_str)
        if module in cls._equipment_imported_modules:
            cls._equipment_imported_modules.remove(module)
            module = importlib.reload(module)
        cls._equipment_imported_modules.append(module)
        cls._equipments_proxies[id] = EquipmentProxy(getattr(module, eCls))

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
    Runtime management of Experiments
    """
    _experiment_proxies: dict[str, ExperimentProxy] = {}
    _experiment_imported_modules: list[ModuleType] = []

    @classmethod
    def createExperiment(cls, id: str, module_str: str, eCls: str):
        with cls.handler_experiment_id_lock:
            cls.handler_experiment_id = id

            module = importlib.import_module(module_str)
            if module in cls._experiment_imported_modules:
                cls._experiment_imported_modules.remove(module)
                module = importlib.reload(module)
            cls._experiment_imported_modules.append(module)

            cls._experiment_proxies[id] = ExperimentProxy(
                id=id,
                experimentCls=getattr(module, eCls),
                manager=cls,
                loop=asyncio.get_event_loop(),
            )

    @classmethod
    def getExperimentParams(cls, id: str):
        return cls._experiment_proxies[id].params

    @classmethod
    def getExperimentLoopCount(cls):
        return cls._experiment_proxies[id].loop_count

    @classmethod
    def setExperimentParams(cls, id: str, params: Params):
        cls._experiment_proxies[id].params = params

    @classmethod
    def removeExperiment(cls, id: str):
        if id not in cls._experiment_proxies:
            return

        # experiment should already be stopped
        if not cls._experiment_proxies[id].stopped():
            return

        del cls._experiment_proxies[id]

        # TODO run clean up of extensions

        if id in cls._chart_proxies:
            del cls._chart_proxies[id]

        if id in cls._sql_saver_proxies:
            del cls._sql_saver_proxies[id]

    @classmethod
    def startExperiment(cls, id: str):
        cls._experiment_proxies[id].start()

    @classmethod
    def getStreamingLoopCount(cls, id: str):
        return cls._experiment_proxies[id].getStreamingLoopCount()

    @classmethod
    def pauseExperiment(cls, id: str):
        cls._experiment_proxies[id].pause()

    @classmethod
    def continueExperiment(cls, id: str):
        cls._experiment_proxies[id].unpause()

    @classmethod
    def stopExperiment(cls, id: str):
        cls._experiment_proxies[id].stop()

    """
    Extension Management
    """
    handler_experiment_id_lock: Lock = Lock()
    handler_experiment_id: str

    @classmethod
    def initializeExtensions(cls, experiment_id: str):
        # Initialize the charts
        if experiment_id in cls._chart_proxies:
            for chart_proxy in cls._chart_proxies[experiment_id].values():
                chart_proxy.initialize()

        # Initialize sql savers
        if experiment_id in cls._sql_saver_proxies:
            for sql_saver_proxy in cls._sql_saver_proxies[experiment_id].values():
                sql_saver_proxy.initialize()

    """
    Chart management
    """

    # Manages charts by experiment id and chart name
    _chart_proxies: dict[str, dict[str, ChartProxy]] = {}

    @classmethod
    @override
    def createChart(cls, chartT: ChartABC, kwargs: Any = {}):
        # The title should be unique
        title = kwargs["title"]

        if cls.handler_experiment_id not in cls._chart_proxies:
            cls._chart_proxies[cls.handler_experiment_id] = {}

        cls._chart_proxies[cls.handler_experiment_id][title] = ChartProxy(
            experiment_id=cls.handler_experiment_id,
            title=title,
            chartT=chartT,
            kwargs=kwargs,
        )
        return cls._chart_proxies[cls.handler_experiment_id][title].chart

    """
    Sqlsaver management
    """

    # Manages sql savers by experiment id and sql_saver name
    _sql_saver_proxies: dict[str, dict[str, SqlSaverProxy]] = {}

    @classmethod
    @override
    def createSqlSaver(cls, sql_saverT: type[SqlSaverABC], kwargs: Any = {}):
        title = kwargs["title"]

        if cls.handler_experiment_id not in cls._sql_saver_proxies:
            cls._sql_saver_proxies[cls.handler_experiment_id] = {}

        cls._sql_saver_proxies[cls.handler_experiment_id][title] = SqlSaverProxy(
            experiment_id=cls.handler_experiment_id,
            title=title,
            sql_saverT=sql_saverT,
            worker=SqlWorker,
            kwargs=kwargs,
        )

        return cls._sql_saver_proxies[cls.handler_experiment_id][title].sql_saver
