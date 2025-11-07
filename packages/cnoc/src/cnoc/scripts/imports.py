import importlib
import inspect
import json
import pkgutil
import sys
from traceback import print_tb
from typing import Any, TypedDict

from .utils import Runtime, preloadLocal


from ..public.equipment import EquipmentABC
from ..public.experiment import ExperimentABC

runtime = Runtime()


def eeImports(
    eetype: type[ExperimentABC[Any]] | type[EquipmentABC[Any]],
    names: list[str],
    local_names: list[str],
):
    class ReturnType(TypedDict):
        module: str
        cls: str

    res: dict[type[ExperimentABC[Any]] | type[EquipmentABC[Any]], ReturnType] = {}

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
                    runtime.printErr(
                        f"Duplicate class {cls} found in {name}, already imported from {res[clsT]['module']}"
                    )
        except ModuleNotFoundError:
            return
        except Exception as e:
            runtime.printErr(
                f"Failed to import package {name} from {src} for {eetype.__name__}: {e}"
            )
            _, _, traceback = sys.exc_info()
            print_tb(traceback, file=sys.stderr)
            runtime.errFlush()

    def onerror(x: str):
        if x not in names or x not in local_names:
            return

        print(f"Error importing module {x} while walk_packages ", file=sys.stderr)
        _, _, traceback = sys.exc_info()
        print_tb(traceback, file=sys.stderr)
        runtime.errFlush()

    for name in names:
        try:
            pkg = importlib.import_module(name)
        except Exception as e:
            runtime.printErr(
                f"Failed to import module {name} from names for {eetype.__name__}: {e}"
            )
            continue

        for package in pkgutil.walk_packages(
            pkg.__path__, pkg.__name__ + ".", onerror=onerror
        ):
            examinePackage(name, package.name)

    for package in pkgutil.walk_packages(onerror=onerror):
        for name in local_names:
            if package.name.startswith(name):
                examinePackage(name, package.name)
                break

    return list(res.values())


def main():
    try:
        local_names = preloadLocal()

        match sys.argv[1]:
            case "equipment":
                runtime.printResult(
                    json.dumps(eeImports(EquipmentABC, sys.argv[2:], local_names))
                )
            case "experiment":
                runtime.printResult(
                    json.dumps(eeImports(ExperimentABC, sys.argv[2:], local_names))
                )
            case _:
                runtime.printErr(f"Invalid argument {sys.argv[1]}")

    except Exception as e:
        runtime.printErr(f"Error: {e}")
        _, _, traceback = sys.exc_info()
        print_tb(traceback, file=sys.stderr)
        runtime.errFlush()

    runtime.end()
