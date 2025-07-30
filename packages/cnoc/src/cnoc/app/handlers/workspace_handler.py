import importlib
import inspect
import json
import pkgutil
from typing import TypedDict

from ..state.experiments import Experiments

from ..state.foundation import Foundation

from ...public.params import (
    AllParamTypes,
    CompositeParam,
    InstanceEquipmentParam,
    InstanceExperimentParam,
)

from ..state.equipments import Equipments

from ...public.equipment import EquipmentABC
from ...public.experiment import ExperimentABC
from websockets import ServerConnection


def eeImports[T: type[ExperimentABC] | type[EquipmentABC]](eetype: T, names: list[str]):
    class ReturnType(TypedDict):
        module: str
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
                    res[clsT] = {"module": name, "cls": cls}
                else:
                    print(
                        f"Duplicate class {cls} found in {name}, already imported from {res[clsT]['module']}",
                        flush=True,
                    )
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


def putParamsInstance(params: dict[str, AllParamTypes]):
    for k in params.keys():
        if params[k]._type == CompositeParam._type:
            putParamsInstance(params[k].children)
            continue

        if params[k]._type == InstanceEquipmentParam._type:
            params[k].instance = Equipments.instances[params[k].name].instance
            continue

        if params[k]._type == InstanceExperimentParam._type:
            params[k].instance = Experiments.instances[params[k].name].instance
            continue


async def workspaceHandler(ws: ServerConnection):
    Foundation.workspace_ws = ws
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
                await ws.send(
                    json.dumps(
                        {
                            "command": "equipment:create",
                            "value": {
                                "module": req["value"]["module"],
                                "cls": req["value"]["cls"],
                                "name": req["value"]["name"],
                                "params": Equipments.create(
                                    name=req["value"]["name"],
                                    module_str=req["value"]["module"],
                                    cls_str=req["value"]["cls"],
                                ),
                            },
                        }
                    )
                )

            case "equipment:save":
                Equipments.save(
                    name=req["value"]["name"], params=req["value"]["params"]
                )
                putParamsInstance(
                    Equipments.instances[req["value"]["name"]].instance.params
                )

                await ws.send(
                    json.dumps({"command": "equipment:save", "value": Equipments})
                )

            case "equipment:remove":
                Equipments.remove(req["value"]["name"])
                await ws.send(
                    json.dumps(
                        {"command": "equipment:remove", "value": req["value"]["name"]}
                    )
                )

            case "experiment:create":
                await ws.send(
                    json.dumps(
                        {
                            "command": "equipment:create",
                            "value": {
                                "module": req["value"]["module"],
                                "cls": req["value"]["cls"],
                                "name": req["value"]["name"],
                                "params": Experiments.create(
                                    name=req["value"]["name"],
                                    module_str=req["value"]["module"],
                                    cls_str=req["value"]["cls"],
                                ),
                            },
                        }
                    )
                )
                pass
            # case "set_params":
            #     State.setParams(req["id"], ParamModels2Params(req["params"]))
            #     break
