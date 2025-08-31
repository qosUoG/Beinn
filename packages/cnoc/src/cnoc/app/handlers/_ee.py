import importlib
import inspect
import json
import pkgutil


from struct import pack
import sys

from traceback import print_tb
from typing import Any, Literal, TypedDict
from websockets import ServerConnection

from ...public.params import (
    AllParamTypes,
    CompositeParam,
    InstanceEquipmentParam,
    cnoc_params2Dict,
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
            continue

        for package in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
            examinePackage("walk_packages", package.name)

    def onerror(x: str):
        print(f"Error importing module {x} while walk_packages ")
        _, _, traceback = sys.exc_info()
        print_tb(traceback)
        print(end=None, flush=True)

    roots: list[str]
    if "/" in __file__:
        roots = __file__.split("/")
    elif "\\" in __file__:
        roots = __file__.split("\\")
    else:
        roots = [__file__]
    venv_index = roots.index(".venv")
    path = "/".join(roots[:venv_index])

    for package in pkgutil.walk_packages([path], onerror=onerror):
        examinePackage(path, package.name)

    return list(res.values())


def imports(
    eetype: Literal["equipment"] | Literal["experiment"],
    packages: list[str],
):
    print(packages, flush=True)
    return (
        eeImports(
            EquipmentABC if eetype == "equipment" else ExperimentABC,
            packages,
        ),
    )


class CreateType(TypedDict):
    name: str
    module: str
    cls: str


def create(
    eetype: Literal["equipment"] | Literal["experiment"],
    value: list[CreateType],
):
    res: list[dict[str, Any]] = []
    for v in value:
        try:
            instance = (
                Equipments.create(
                    name=v["name"], module_str=v["module"], cls_str=v["cls"]
                )
                if eetype == "equipment"
                else Experiments.create(
                    name=v["name"], module_str=v["module"], cls_str=v["cls"]
                )
            )

            res.append(
                {
                    "success": True,
                    "instance": {
                        "module": v["module"],
                        "cls": v["cls"],
                        "name": v["name"],
                        "params": cnoc_params2Dict(instance.instance.params),  # type: ignore
                    },
                }
            )
        except Exception:
            res.append(
                {
                    "success": False,
                    "instance": {
                        "module": v["module"],
                        "cls": v["cls"],
                        "name": v["name"],
                    },
                }
            )

    return res


def putParamsInstance(params: dict[str, AllParamTypes]):
    for k in params.keys():
        if params[k].type == CompositeParam.type:
            putParamsInstance(params[k].children)
            continue

        try:
            if (
                params[k].type == InstanceEquipmentParam.type
                and params[k].name is not None
            ):
                params[k].instance = Equipments.instances[params[k].name].instance
                continue

            # if (
            #     params[k].type == InstanceExperimentParam.type
            #     and params[k].name is not None
            # ):
            #     params[k].instance = Experiments.instances[params[k].name].instance
            #     continue

        except KeyError:
            print(
                f"Param {k} of type {params[k].type} with name {params[k].name} does not exist",
                flush=True,
            )


class UpdateParamsType(TypedDict):
    name: str
    params: dict[str, AllParamTypes]


def updateParams(
    eetype: Literal["equipment"] | Literal["experiment"],
    value: list[UpdateParamsType],
):
    res: list[dict[str, Any]] = []
    for v in value:
        if eetype == "equipment":
            Equipments.updateParams(name=v["name"], params=v["params"])
            putParamsInstance(Equipments.instances[v["name"]].instance.params)

            res.append(
                {
                    "name": v["name"],
                    "params": cnoc_params2Dict(
                        Equipments.instances[v["name"]].instance.params
                    ),
                }
            )
        elif eetype == "experiment":
            Experiments.updateParams(name=v["name"], params=v["params"])
            putParamsInstance(Experiments.instances[v["name"]].instance.params)

            res.append(
                {
                    "name": v["name"],
                    "params": cnoc_params2Dict(
                        Experiments.instances[v["name"]].instance.params
                    ),
                }
            )

    return res


def remove(
    eetype: Literal["equipment"] | Literal["experiment"],
    names: list[str],
):
    for name in names:
        if eetype == "equipment":
            Equipments.remove(name)
        else:
            Experiments.remove(name)

    return names


async def result(ws: ServerConnection, id: str, command: str, value: Any):
    await ws.send(json.dumps({"command": command, "value": value, "id": id}))


def getEEFn(eetype: Literal["equipment"] | Literal["experiment"]):
    return {
        f"{eetype}:imports": lambda ws, id, value: result(
            ws, id, f"{eetype}:imports", imports(eetype, value)
        ),
        f"{eetype}:create": lambda ws, id, value,: result(
            ws, id, f"{eetype}:create", create(eetype, value)
        ),
        f"{eetype}:update_params": lambda ws, id, value: result(
            ws, id, f"{eetype}:update_params", updateParams(eetype, value)
        ),
        f"{eetype}:remove": lambda ws, id, value: result(
            ws, id, f"{eetype}:remove", remove(eetype, value)
        ),
    }


handlers = {**getEEFn("equipment"), **getEEFn("experiment")}
