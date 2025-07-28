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


def eeImports[T: type[ExperimentABC] | type[EquipmentABC]](eetype: T, names: list[str]):
    class ReturnType(TypedDict):
        modules: list[str]
        cls: str

    res: dict[T, ReturnType] = {}

    def examinePackage(src: str, name: str):
        try:
            for [cls, clsT] in inspect.getmembers(
                importlib.import_module(name), inspect.isclass
            ):
                if (
                    not issubclass(clsT, eetype)
                    or clsT is eetype
                    or clsT.__module__ != name
                ):
                    continue

                if clsT not in res:
                    res[clsT] = {"modules": [name], "cls": cls}
                else:
                    res[clsT]["modules"].append(name)
        except ModuleNotFoundError:
            return
        except Exception as e:
            print(
                f"Failed to import package {package.name} from {src} for {eetype.__name__}: {e}",
                flush=True,
            )

    for name in names:
        try:
            pkg = importlib.import_module(name)
        except Exception as e:
            print(
                f"Failed to import module {name} from names for {eetype.__name__}: {e}",
                flush=True,
            )

        for package in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
            examinePackage("walk_packages", package.name)

    for package in pkgutil.walk_packages(["."]):
        examinePackage(".", package.name)

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
