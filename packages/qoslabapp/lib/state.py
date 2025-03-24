import asyncio
import importlib
from threading import Event, Lock


from types import ModuleType
from typing import Any, AsyncGenerator, Callable, override


from fastapi import WebSocket

from qoslablib.extensions import chart
from qoslablib.extensions.chart import ChartABC, ChartConfigABC, ChartManagerABC
from qoslablib.extensions.saver import (
    SqlSaverABC,
    SqlSaverConfigABC,
    SqlSaverManagerABC,
)
from qoslablib.params import Params

from ..lib.utils import singleKVDictMessage


from .workers.sqlite3 import SqlWorker

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
    handler_experiment_id_lock: Lock = Lock()
    handler_experiment_id: str

    @classmethod
    def initializeExtensions(
        cls, experiment_id: str, sendObjMessage: Callable[[str, dict[str, Any]], None]
    ):
        # Initialize and send configs of the charts
        chart_configs: dict[str, ChartConfigABC] = {}
        if experiment_id in cls._chart_proxies:
            for [chart_title, chart_proxy] in cls._chart_proxies[experiment_id].items():
                chart_proxy.initialize()
                chart_configs[chart_title] = chart_proxy.getConfig()

        if chart_configs:
            sendObjMessage("chart_configs", chart_configs)

        # Initialize sql savers and send configs of the sql savers
        sql_saver_configs: dict[str, SqlSaverConfigABC] = {}
        if experiment_id in cls._sql_saver_proxies:
            for [sql_saver_title, sql_saver_proxy] in cls._sql_saver_proxies[
                experiment_id
            ].items():
                sql_saver_proxy.initialize()
                sql_saver_configs[sql_saver_title] = SqlSaverProxy.getConfig()

        if sql_saver_configs:
            sendObjMessage("sql_saver_configs", sql_saver_configs)

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
            if cls.handler_experiment_id not in cls._chart_proxies:
                cls._chart_proxies[cls.handler_experiment_id] = {}

            cls._chart_proxies[cls.handler_experiment_id][title] = ChartProxy(
                experiment_id=cls.handler_experiment_id,
                title=title,
                chartT=chartT,
                kwargs=kwargs,
            )
            return cls._chart_proxies[cls.handler_experiment_id][title]._chart

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
            if cls.handler_experiment_id not in cls._sql_saver_proxies:
                cls._sql_saver_proxies[cls.handler_experiment_id] = {}

            cls._sql_saver_proxies[cls.handler_experiment_id][title] = SqlSaverProxy(
                experiment_id=cls.handler_experiment_id,
                title=title,
                sql_saverT=sql_saverT,
                kwargs=kwargs,
            )

            return cls._sql_saver_proxies[cls.handler_experiment_id][title]._sql_saver
