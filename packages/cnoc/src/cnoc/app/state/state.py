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

    _equipmentproxies: dict[str, EquipmentProxy[EquipmentABC]] = {}
    _equipment_imported_modules: list[ModuleType] = []

    _experimentproxies: dict[str, ExperimentProxy] = {}
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
                cls._equipmentproxies[id] = EquipmentProxy(getattr(module, ecls_str))
            case "experiment":
                module = _importModule(cls._experiment_imported_modules, module_str)
                cls._experimentproxies[id] = ExperimentProxy(getattr(module, ecls_str))

    # TODO Handle should not be removed yet
    @classmethod
    def remove(cls, id: str):
        if id in cls._equipmentproxies:
            del cls._equipmentproxies[id]
            return
        if id in cls._experimentproxies:
            del cls._experimentproxies[id]

    @classmethod
    def setParams(cls, id: str, params: Params):
        if id in cls._equipmentproxies:
            with cls._equipmentproxies[id].lock() as equipment:
                equipment.params = params
            return
        if id in cls._experimentproxies:
            cls._experimentproxies[id].params = params

    """
    Experiment handler interface
    """

    @classmethod
    def get(cls, id: str):
        if id in cls._experimentproxies:
            return cls._experimentproxies[id]

    @classmethod
    def start(cls, id: str):
        if id in cls._experimentproxies:
            cls._experimentproxies[id].start()

    @classmethod
    def pause(cls, id: str):
        if id in cls._experimentproxies:
            cls._experimentproxies[id].pause()

    @classmethod
    def unpause(cls, id: str):
        if id in cls._experimentproxies:
            cls._experimentproxies[id].unpause()

    @classmethod
    def stop(cls, id: str):
        if id in cls._experimentproxies:
            cls._experimentproxies[id].stop()

    @classmethod
    def subscribeExperimentMessage(cls, id: str, ws: ServerConnection):
        return cls._experimentproxies[id].subscribeMessage(ws)

    """Experiment Extensions"""

    @classmethod
    def subscribeChart(cls, id: str, title: str, ws: ServerConnection):
        return cls._experimentproxies[id].subscribeChart(title, ws)

    """App Life cycle"""

    @classmethod
    async def kill(cls):
        """This function is meant to be stopping gracefully. Timeout should be handled outside of this function"""

        # First stop async for each function
        coros: list[CoroutineType[Any, Any, Any]] = []
        for experiment_proxy in cls._experimentproxies.values():
            coros.append(experiment_proxy.kill())

        for equipment_proxy in cls._equipmentproxies.values():
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
        return cls._equipmentproxies[id].interpret(code, name)
