import asyncio
from contextlib import redirect_stderr, redirect_stdout
import importlib
from io import StringIO
from re import L
import sys
from types import CoroutineType, ModuleType
from typing import Any, Literal

from ...public.params import Params
from ...public.equipment import EquipmentABC
from websockets import ServerConnection

from ..proxies.experiment import ExperimentProxy
from ..proxies.equipment import EquipmentProxy


def _importModule(
    list: list[ModuleType],
    module_str: str,
):
    module = importlib.import_module(module_str)
    if module in list:
        list.remove(module)
        module = importlib.reload(module)
    list.append(module)
    return module


class State:
    """workspace_handler interface"""

    _equipment_proxies: dict[str, EquipmentProxy[EquipmentABC]] = {}
    _equipment_imported_modules: list[ModuleType] = []

    _experiment_proxies: dict[str, ExperimentProxy] = {}
    _experiment_imported_modules: list[ModuleType] = []

    @classmethod
    def create(
        cls,
        eetype: Literal["equipment", "experiment"],
        id: str,
        module_str: str,
        ecls_str: str,
    ):
        match eetype:
            case "equipment":
                module = _importModule(cls._equipment_imported_modules, module_str)
                cls._equipment_proxies[id] = EquipmentProxy(getattr(module, ecls_str))
            case "experiment":
                module = _importModule(cls._experiment_imported_modules, module_str)
                cls._experiment_proxies[id] = ExperimentProxy(getattr(module, ecls_str))

    # TODO Handle should not be removed yet
    @classmethod
    def remove(cls, id: str):
        if id in cls._equipment_proxies:
            del cls._equipment_proxies[id]
            return
        if id in cls._experiment_proxies:
            del cls._experiment_proxies[id]

    @classmethod
    def setParams(cls, id: str, params: Params):
        if id in cls._equipment_proxies:
            with cls._equipment_proxies[id].lock() as equipment:
                equipment.params = params
            return
        if id in cls._experiment_proxies:
            cls._experiment_proxies[id].params = params

    """
    Experiment handler interface
    """

    @classmethod
    def get(cls, id: str):
        if id in cls._experiment_proxies:
            return cls._experiment_proxies[id]

    @classmethod
    def start(cls, id: str):
        if id in cls._experiment_proxies:
            cls._experiment_proxies[id].start()

    @classmethod
    def pause(cls, id: str):
        if id in cls._experiment_proxies:
            cls._experiment_proxies[id].pause()

    @classmethod
    def unpause(cls, id: str):
        if id in cls._experiment_proxies:
            cls._experiment_proxies[id].unpause()

    @classmethod
    def stop(cls, id: str):
        if id in cls._experiment_proxies:
            cls._experiment_proxies[id].stop()

    @classmethod
    def subscribeExperimentMessage(cls, id: str, ws: ServerConnection):
        return cls._experiment_proxies[id].subscribeMessage(ws)

    """Experiment Extensions"""

    @classmethod
    def subscribeChart(cls, id: str, title: str, ws: ServerConnection):
        return cls._experiment_proxies[id].subscribeChart(title, ws)

    """App Life cycle"""

    @classmethod
    async def kill(cls):
        """This function is meant to be stopping gracefully. Timeout should be handled outside of this function"""

        # First stop async for each function
        coros: list[CoroutineType[Any, Any, Any]] = []
        for experiment_proxy in cls._experiment_proxies.values():
            coros.append(experiment_proxy.kill())

        for equipment_proxy in cls._equipment_proxies.values():
            equipment_proxy.cleanup()

        await asyncio.gather(*coros, SqlWorker.stop())

    """CLI"""

    @classmethod
    def interpret(cls, code: str):
        try:
            return {
                "type": "eval",
                "result": f"{eval(code, globals=globals())}",
            }

        except SyntaxError:
            pass
        except Exception as e:
            return {
                "type": "error",
                "result": f"code: {code}, error:{e}",
            }

        try:
            f = StringIO()

            with redirect_stdout(f):
                with redirect_stderr(sys.stdout):
                    exec(code, globals=globals())

            return {
                "type": "exec",
                "result": f.getvalue(),
            }

        except Exception as e:
            return {
                "type": "error",
                "result": f"code: {code}, error:{e}",
            }

    @classmethod
    def eqiupment_interpret(cls, *, id: str, name: str, code: str, type: str):
        return cls._equipment_proxies[id].interpret(code, name)
