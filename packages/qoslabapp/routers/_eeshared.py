import importlib
import importlib.util
import inspect
import pkgutil
from typing import Literal, TypedDict
import warnings

from qoslablib.params import AllParamTypes
from qoslablib.runtime import EquipmentABC, ExperimentABC


from ..lib.state import AppState

type EELiteral = Literal["equipment"] | Literal["experiment"]
type EEABC = type[ExperimentABC] | type[EquipmentABC]


def getAvailableEEs(eeABC: EEABC, names: list[str]):
    class ReturnType(TypedDict):
        modules: list[str]
        cls: str

    ees: (
        dict[type[ExperimentABC], ReturnType] | dict[type[EquipmentABC], ReturnType]
    ) = {}

    warnings.filterwarnings("ignore")

    # Check all possible paths
    for package in pkgutil.walk_packages():
        for module in names:
            # Only search for declared dependencies
            if not package.name.startswith(module):
                continue

            # Check that the module is importable
            if not importlib.util.find_spec(module):
                continue

            # Exclude these
            if package.name.endswith("__main__"):
                continue

            try:
                for [cls, clsT] in inspect.getmembers(
                    importlib.import_module(package.name), inspect.isclass
                ):
                    if (
                        not issubclass(clsT, eeABC)
                        or clsT is ExperimentABC
                        or clsT is EquipmentABC
                    ):
                        continue

                    if clsT not in ees:
                        ees[clsT] = {"modules": [package.name], "cls": cls}
                    else:
                        ees[clsT]["modules"].append(package.name)

            except ModuleNotFoundError:
                pass
            except Exception as e:
                print(f"Path {package.name} produced an exception")
                print(e)
                break

    warnings.filterwarnings("default")

    return list(ees.values())


def populateParam(param: AllParamTypes):
    match param.type:
        case "instance.equipment":
            param.instance = AppState._equipments_proxies[param.instance_id]

        case "instance.experiment":
            raise Exception("Playlist is not being implemented yet")
            # param.instance = AppState._experiment_proxies[param.instance_id]

        # case "composite":
        #     # Recursively instantiate params
        #     for [child_name, child_param] in param.children.items():
        #         param.children[child_name] = populateParam(child_param)

    return param
