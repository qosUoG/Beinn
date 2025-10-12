import importlib
import inspect
import pkgutil
import site
import sys
from traceback import print_tb
from typing import TypedDict


from ..public.equipment import EquipmentABC
from ..public.experiment import ExperimentABC


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


def main():
    roots: list[str]
    if "/" in __file__:
        roots = __file__.split("/")
    elif "\\" in __file__:
        roots = __file__.split("\\")
    venv_index = roots.index(".venv")
    path = "/".join(roots[:venv_index])

    site.addsitedir(path)

    match sys.argv[1]:
        case "equipment":
            return eeImports(EquipmentABC, sys.argv[2:])
        case "experiment":
            return eeImports(ExperimentABC, sys.argv[2:])
