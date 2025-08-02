import importlib
import inspect
import json
import pkgutil
import pprint
import sys
from traceback import print_tb
from typing import Literal, TypedDict
from websockets import ServerConnection

from ...public.params import (
    AllParamTypes,
    CompositeParam,
    InstanceEquipmentParam,
    InstanceExperimentParam,
    param2Dict,
)

from ..state.experiments import Experiments

from ..state.equipments import Equipments

from ...public.equipment import EquipmentABC

from ...public.experiment import ExperimentABC


def eeImports(eetype: type[ExperimentABC] | type[EquipmentABC], names: list[str]):
    class ReturnType(TypedDict):
        module: str
        cls: str

    res: dict[type[ExperimentABC] | type[EquipmentABC], ReturnType] = {}

    def examinePackage(src: str, name: str):
        print(name, flush=True)
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

                print(f"{cls}, {clsT.__module__}", flush=True)
                print(f"{clsT.__module__}, {name}", flush=True)

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
                f"Failed to import package {name} from {src} for {eetype.__name__}: {e}",
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

    roots = __file__.split("/")
    venv_index = roots.index(".venv")
    path = "/".join(roots[:venv_index])
    print(path, flush=True)

    def onerror(x):
        print("Error importing module %s" % x)
        _, _, traceback = sys.exc_info()
        print_tb(traceback)

    for package in pkgutil.walk_packages(
        [path], roots[venv_index - 1] + ".", onerror=onerror
    ):
        pprint.pprint(package)
        print(flush=True)
        examinePackage(path, package.name)

    return list(res.values())


async def imports(
    ws: ServerConnection,
    eetype: Literal["equipment"] | Literal["experiment"],
    packages: list[str],
):
    await ws.send(
        json.dumps(
            {
                "command": f"{eetype}:imports",
                "value": eeImports(
                    EquipmentABC if eetype == "equipment" else ExperimentABC, packages
                ),
            }
        )
    )


async def create(
    ws: ServerConnection,
    eetype: Literal["equipment"] | Literal["experiment"],
    name: str,
    module: str,
    cls: str,
):
    instance = (
        Equipments.create(name=name, module_str=module, cls_str=cls)
        if eetype == "equipment"
        else Experiments.create(name=name, module_str=module, cls_str=cls)
    )

    await ws.send(
        json.dumps(
            {
                "command": "equipment:create",
                "value": {
                    "module": module,
                    "cls": cls,
                    "name": name,
                    "params": param2Dict(instance.instance.params),
                },
            }
        )
    )


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


async def updateParams(
    ws: ServerConnection,
    eetype: Literal["equipment"] | Literal["experiment"],
    name: str,
    params: dict[str, AllParamTypes],
):
    if eetype == "equipment":
        Equipments.save(name=name, params=params)
        putParamsInstance(Equipments.instances[name].instance.params)

        await ws.send(json.dumps({"command": "equipment:save", "value": Equipments}))

    elif eetype == "experiment":
        Experiments.save(name=name, params=params)
        putParamsInstance(Experiments.instances[name].instance.params)

        await ws.send(json.dumps({"command": "experiment:save", "value": Experiments}))


async def remove(
    ws: ServerConnection,
    eetype: Literal["equipment"] | Literal["experiment"],
    name: str,
):
    if eetype == "equipment":
        Equipments.remove(name)
    else:
        Experiments.remove(name)

    await ws.send(json.dumps({"command": f"{eetype}:remove", "value": name}))


def getEEFn(eetype: Literal["equipment"] | Literal["experiment"]):
    return {
        f"{eetype}:imports": lambda ws, value: imports(ws, eetype, value["packages"]),
        f"{eetype}:create": lambda ws, value,: create(
            ws, eetype, value["name"], value["module"], value["cls"]
        ),
        f"{eetype}:params": lambda ws, value: updateParams(
            ws, eetype, value["name"], value["params"]
        ),
        f"{eetype}:remove": lambda ws, value: remove(ws, eetype, value["name"]),
    }


handlers = {**getEEFn("equipment"), **getEEFn("experiment")}
