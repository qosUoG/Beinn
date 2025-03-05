import importlib.util
import pkgutil

import warnings

from fastapi import APIRouter

import importlib
import inspect
from pydantic import BaseModel
from qoslablib import labtype as l
from ..lib.state import AppState
from ..lib.utils import importFromStr


router = APIRouter()


class Path(BaseModel):
    path: str


class StartExperimentsPayload(BaseModel):
    equipments: list[l.Equipment]
    experiments: list[l.Experiment]


@router.post("/workspace/start_experiments")
async def start_experiments(body: StartExperimentsPayload):
    AppState.reset_dicts()

    # Instantiate equipments
    for equipment in body.equipments:
        with open(equipment.path, mode="r", encoding="utf-8") as raw:
            # Read the definition code from the source file
            [module, classname] = importFromStr(raw.read())
            _class = getattr(module, classname)
            # Initilize the equipment and assign to equipments dict
            AppState.equipments[equipment.name] = _class(equipment.params)

    # Assign instance params to each param
    for equipment in AppState.equipments.values():
        for p in equipment.params.values():
            if p.type == "instance":
                p.instance = AppState.equipments[p.instance_name]

    # Instantiate experiments
    for experiment in body.experiments:
        with open(experiment.path, mode="r", encoding="utf-8") as raw:
            # Read the definition code from the source file
            [module, classname] = importFromStr(raw.read())
            _class = getattr(module, classname)
            # put in equipment instances into params

            for [_, p] in experiment.params.items():
                if p.type == "instance":
                    p.instance = AppState.equipments[p.instance_name]

            # Initilize the experiment and assign to experiments dict
            AppState.register_experiment(experiment.name, experiment.params, _class)

    # Start all the threads
    AppState.start_experiments()


class AvailableEquipmentsPayload(BaseModel):
    names: list[str]


@router.post("/workspace/available_equipments")
async def available_equipments(payload: AvailableEquipmentsPayload):
    class EquipmentModule(BaseModel):
        module: str
        cls: str

    equipments: list[EquipmentModule] = []

    warnings.filterwarnings("ignore")

    def get_equipments(module: str):
        # First check the module is importable
        if importlib.util.find_spec(module) and not module.endswith("__main__"):
            try:
                for [cls, clsT] in inspect.getmembers(importlib.import_module(module)):
                    if hasattr(clsT, "equipment_params"):
                        equipments.append({"module": module, "cls": cls})
            except Exception as e:
                print(f"Path {module} produced an exception")
                print(e)

    # Check all possible paths
    for package in pkgutil.walk_packages():
        for n in payload.names:
            if package.name.startswith(n):
                get_equipments(package.name)
                break

    # TODO Check in local directory for project specific equipments

    warnings.filterwarnings("default")
    return equipments


class AvailableExperimentsPayload(BaseModel):
    names: list[str]


@router.post("/workspace/available_experiments")
async def available_experiments(payload: AvailableExperimentsPayload):
    class ExperimentModule(BaseModel):
        module: str
        cls: str

    experiments: list[ExperimentModule] = []

    warnings.filterwarnings("ignore")

    def get_experiments(module: str):
        # First check the module is importable
        if importlib.util.find_spec(module) and not module.endswith("__main__"):
            try:
                for [cls, clsT] in inspect.getmembers(importlib.import_module(module)):
                    if hasattr(clsT, "experiment_params"):
                        experiments.append({"module": module, "cls": cls})
            except Exception as e:
                print(f"Path {module} produced an exception")
                print(e)

    # Check all possible paths
    for package in pkgutil.walk_packages():
        for n in payload.names:
            if package.name.startswith(n):
                get_experiments(package.name)
                break

    # TODO Check in local directory for project specific experiments

    warnings.filterwarnings("default")
    return experiments
