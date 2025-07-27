import importlib
import inspect
import json
import pkgutil
from struct import pack
from typing import TypedDict
import warnings

# from ...public.params import ParamModels2Params

# from ..state.state import State

from ...public.equipment import EquipmentABC
from ...public.experiment import ExperimentABC
from websockets import ServerConnection

commands = {}


def eeImports[T: type[ExperimentABC] | type[EquipmentABC]](eetype: T):
    class ReturnType(TypedDict):
        modules: list[str]
        cls: str

    res: dict[T, ReturnType] = {}

    warnings.filterwarnings("ignore")

    # Check all possible paths
    for package in pkgutil.walk_packages():
        # Exclude these

        if package.name.startswith("_"):
            continue
        if package.name.startswith("__"):
            continue
        if package.name.endswith("__main__"):
            continue

        try:
            for [cls, clsT] in inspect.getmembers(
                importlib.import_module(package.name), inspect.isclass
            ):
                print(package.name + "\n")
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


async def workspaceHandler(ws: ServerConnection):
    async for message in ws:
        req = json.loads(message)
        command: str = req["command"]
        match command:
            case "equipment:imports":
                await ws.send(
                    json.dumps(
                        {
                            "command": "equipment:imports",
                            "value": eeImports(EquipmentABC),
                        }
                    )
                )
                break
            case "experiment:imports":
                await ws.send(
                    json.dumps(
                        {
                            "command": "experiment:imports",
                            "value": eeImports(ExperimentABC),
                        }
                    )
                )
                break
            case "equipment:create":
                # State.create("equipment", req["id"], req["module"], req["cls"])
                pass
            case "experiment:create":
                # State.create("experiment", req["id"], req["module"], req["cls"])
                pass
            # case "set_params":
            #     State.setParams(req["id"], ParamModels2Params(req["params"]))
            #     break
