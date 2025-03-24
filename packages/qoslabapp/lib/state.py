import asyncio
from contextlib import contextmanager
import importlib
from threading import Lock


from types import ModuleType
from typing import Any, Callable, override


from fastapi import WebSocket


from qoslablib.extensions.chart import ChartABC, ChartManagerABC
from qoslablib.extensions.saver import (
    SqlSaverABC,
    SqlSaverManagerABC,
)
from qoslablib.params import Params


from .proxies.equipment import EquipmentProxy

from .proxies.experiment import ExperimentProxy

from .proxies.chart import ChartProxy
from .proxies.sql_saver import SqlSaverProxy


class AppState(ChartManagerABC, SqlSaverManagerABC):
    """
    asyncio event loop
    """

    loop: asyncio.EventLoop

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

    @classmethod
    def removeWs(cls, ws: WebSocket):
        cls._ws.remove(ws)

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
        module = importlib.import_module(module_str)
        if module in cls._experiment_imported_modules:
            cls._experiment_imported_modules.remove(module)
            module = importlib.reload(module)
        cls._experiment_imported_modules.append(module)

        cls._experiment_proxies[id] = ExperimentProxy(
            id=id,
            experimentCls=getattr(module, eCls),
            manager=cls,
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
    def getMessageQueueGetFn(cls, id: str):
        return cls._experiment_proxies[id].getMessageQueueGetFn()

    @classmethod
    def pauseExperiment(cls, id: str):
        cls._experiment_proxies[id].pause()

    @classmethod
    def continueExperiment(cls, id: str):
        cls._experiment_proxies[id].unpause()

    @classmethod
    def stopExperiment(cls, id: str):
        cls._experiment_proxies[id].stop()

    @classmethod
    def cancelAllExperiments(cls):
        for proxy in cls._experiment_proxies.values():
            proxy.cancelExperimentTask()

    """
    Extension Management
    """
    current_initializer_lock = Lock()
    current_initializer_id: str
    current_initializer_sendObjMessage: Callable[[str, dict[str, Any]], None]

    @classmethod
    @contextmanager
    def initializeExtensionsAs(
        cls, experiment_id: str, sendObjMessage: Callable[[str, dict[str, Any]], None]
    ):
        try:
            with cls.current_initializer_lock:
                cls.current_initializer_id = experiment_id
                cls.current_initializer_sendObjMessage = sendObjMessage
                yield
        finally:
            pass

    # The following creation methods are run in experiment initialization phase,
    # i.e. not in the main thread
    """
    Chart management
    """

    # Manages charts by experiment id and chart name
    _chart_proxies: dict[str, dict[str, ChartProxy]] = {}
    _chart_proxies_lock = Lock()

    @classmethod
    @override
    def createChart(cls, chartT: ChartABC, kwargs: Any = {}):
        title = kwargs["title"]
        with cls._chart_proxies_lock:
            if cls.current_initializer_id not in cls._chart_proxies:
                cls._chart_proxies[cls.current_initializer_id] = {}

            chart_proxy = ChartProxy(
                experiment_id=cls.current_initializer_id,
                title=title,
                chartT=chartT,
                kwargs=kwargs,
            )

            cls._chart_proxies[cls.current_initializer_id][title] = ChartProxy(
                experiment_id=cls.current_initializer_id,
                title=title,
                chartT=chartT,
                kwargs=kwargs,
            )
            cls.current_initializer_sendObjMessage(
                "chart_config", chart_proxy.getConfig()
            )
            return cls._chart_proxies[cls.current_initializer_id][title]._chart

    @classmethod
    def getChartSubscription(cls, experiment_id: str, title: str):
        if (
            experiment_id not in cls._chart_proxies
            or title not in cls._chart_proxies[experiment_id]
        ):
            return (None, None)

        return cls._chart_proxies[experiment_id][title].subscribe()

    """
    Sqlsaver management
    """

    # Manages sql savers by experiment id and sql_saver name
    _sql_saver_proxies: dict[str, dict[str, SqlSaverProxy]] = {}
    _sql_saver_proxies_lock = Lock()

    @classmethod
    @override
    def createSqlSaver(cls, sql_saverT: type[SqlSaverABC], kwargs: Any = {}):
        title = kwargs["title"]

        with cls._sql_saver_proxies_lock:
            if cls.current_initializer_id not in cls._sql_saver_proxies:
                cls._sql_saver_proxies[cls.current_initializer_id] = {}

            cls._sql_saver_proxies[cls.current_initializer_id][title] = SqlSaverProxy(
                experiment_id=cls.current_initializer_id,
                title=title,
                sql_saverT=sql_saverT,
                kwargs=kwargs,
            )

            return cls._sql_saver_proxies[cls.current_initializer_id][title]._sql_saver
