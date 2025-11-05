import importlib
import inspect
import json
import pkgutil
import sys
from traceback import print_tb
from typing import TypedDict

from .utils import preloadLocal


from ..public.equipment import EquipmentABC
from ..public.experiment import ExperimentABC


def onerror(x: str):
    print(f"Error importing module {x} while walk_packages ")
    _, _, traceback = sys.exc_info()
    print_tb(traceback)
    print(end=None, flush=True)


def eeImports(
    eetype: type[ExperimentABC] | type[EquipmentABC], names: list[str], local_name: str
):
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
            _, _, traceback = sys.exc_info()
            print_tb(traceback)
            print(end=None, flush=True)

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
            examinePackage(name, package.name)

    for package in pkgutil.walk_packages(onerror=onerror):
        if not package.name.startswith(local_name):
            continue

        examinePackage(local_name, package.name)

    return list(res.values())


def main():
    local_name = preloadLocal()

    match sys.argv[1]:
        case "equipment":
            print(json.dumps(eeImports(EquipmentABC, sys.argv[2:], local_name)))
        case "experiment":
            print(json.dumps(eeImports(ExperimentABC, sys.argv[2:], local_name)))
