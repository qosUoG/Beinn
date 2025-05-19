import importlib
import inspect
import json
import pkgutil
from typing import Literal, TypedDict
import warnings

from packages.meall.lib.utils.params import ParamModels2Params

from ..state.state import State
from ...public.equipment import EquipmentABC
from ...public.experiment import ExperimentABC
from websockets import ServerConnection


async def workspaceHandler(ws: ServerConnection):
    async for message in ws:
        req = json.loads(message)
        command: str = req["command"]

        match command:
            case "options:equipment":
                ws.send(json.dumps(eeOptions(EquipmentABC)))
                break
            case "options:experiment":
                ws.send(json.dumps(eeOptions(ExperimentABC)))
                break
            case "create:equipment":
                State.create("equipment", req["id"], req["module"], req["cls"])
                break
            case "create:experiment":
                State.create("equipment", req["id"], req["module"], req["cls"])
                break
            case "set_params":
                State.setParams(req["id"], ParamModels2Params(req["params"]))
                break


def eeOptions[T: type[ExperimentABC] | type[EquipmentABC]](eetype: T):
    class ReturnType(TypedDict):
        modules: list[str]
        cls: str

    res: dict[T, ReturnType] = {}

    warnings.filterwarnings("ignore")

    # Check all possible paths
    for package in pkgutil.walk_packages():
        # Exclude these
        if package.name.endswith("__main__"):
            continue

        try:
            for [cls, clsT] in inspect.getmembers(
                importlib.import_module(package.name), inspect.isclass
            ):
                if not issubclass(clsT, eetype) or clsT is eetype:
                    continue

                if clsT not in res:
                    res[clsT] = {"modules": [package.name], "cls": cls}
                else:
                    res[clsT]["modules"].append(package.name)

        except Exception:
            pass

    warnings.filterwarnings("default")

    return list(res.values())
