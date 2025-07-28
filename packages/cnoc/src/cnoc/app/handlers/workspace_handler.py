import importlib
import inspect
import json
import pkgutil
from typing import TypedDict


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

    # Check all possible paths
    packages.append(".")
    for package in pkgutil.walk_packages(packages):
        print(package.name)
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

        except Exception as e:
            print(
                f"Failed to import package {package.name} for {eetype.__name__}: {e}",
                flush=True,
            )
            continue

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
                            "value": eeImports(EquipmentABC, req["value"]["packages"]),
                        }
                    )
                )

            case "experiment:imports":
                await ws.send(
                    json.dumps(
                        {
                            "command": "experiment:imports",
                            "value": eeImports(ExperimentABC, req["value"]["packages"]),
                        }
                    )
                )

            case "equipment:create":
                # State.create("equipment", req["id"], req["module"], req["cls"])
                pass
            case "experiment:create":
                # State.create("experiment", req["id"], req["module"], req["cls"])
                pass
            # case "set_params":
            #     State.setParams(req["id"], ParamModels2Params(req["params"]))
            #     break
