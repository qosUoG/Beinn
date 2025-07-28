import importlib
import importlib.util
import inspect
import json
import pkgutil
import pprint
from struct import pack
from typing import TypedDict
import warnings

# from ...public.params import ParamModels2Params

# from ..state.state import State

from ...public.equipment import EquipmentABC
from ...public.experiment import ExperimentABC
from websockets import ServerConnection


def eeImports[T: type[ExperimentABC] | type[EquipmentABC]](
    eetype: T, packages: list[str]
):
    class ReturnType(TypedDict):
        modules: list[str]
        cls: str

    res: dict[T, ReturnType] = {}

    warnings.filterwarnings("ignore")

    # Check all possible paths
    for package in packages:
        try:
            for [cls, clsT] in inspect.getmembers(
                importlib.import_module(package), inspect.isclass
            ):
                if not issubclass(clsT, eetype) or clsT is eetype:
                    continue

                if clsT not in res:
                    res[clsT] = {"modules": [package], "cls": cls}
                else:
                    res[clsT]["modules"].append(package)

        except Exception:
            pass

    warnings.filterwarnings("default")

    return list(res.keys())


async def workspaceHandler(ws: ServerConnection):
    print("in handler", flush=True)
    async for message in ws:
        req = json.loads(message)
        pprint.pprint(req)
        print("", flush=True)
        command: str = req["command"]
        match command:
            case "equipment:imports":
                await ws.send(
                    json.dumps(
                        {
                            "command": "equipment:imports",
                            "value": eeImports(EquipmentABC, req["value"]["packages"]),
                        }
                    )
                )
                break
            case "experiment:imports":
                await ws.send(
                    json.dumps(
                        {
                            "command": "experiment:imports",
                            "value": eeImports(ExperimentABC, req["value"]["packages"]),
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
