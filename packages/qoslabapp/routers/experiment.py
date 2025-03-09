import importlib
import inspect
import pkgutil
import warnings
from fastapi import APIRouter
from pydantic import BaseModel
import qoslablib

from ..lib.state import AppState
from qoslablib import labtype as l


router = APIRouter()


class AvailableExperimentsPayload(BaseModel):
    names: list[str]


@router.post("/experiment/available_experiments")
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
                    if issubclass(clsT, qoslablib.runtime.ExpermentABC):
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


class GetParamPayload(BaseModel):
    module: str
    cls: str


@router.post("/experiment/get_params")
async def get_params(payload: GetParamPayload):
    return getattr(
        getattr(importlib.import_module(payload.module), payload.cls),
        "params",
    )


class StartExperimentsPayload(BaseModel):
    equipments: list[l.EquipmentModule]
    experiments: list[l.ExperimentModule]


@router.post("/workspace/start_experiments")
async def start_experiments(body: StartExperimentsPayload):
    # Instantiate equipments
    for equipment in body.equipments:
        # Skip already created equipments
        if equipment.name in AppState.equipments:
            continue

        # Read the definition code from the source file
        _class = getattr(importlib.import_module(equipment.module), equipment.cls)
        # Initilize the equipment and assign to equipments dict
        AppState.equipments[equipment.name] = _class(equipment.params)

    # Replace instances with actual equipments
    for equipment in AppState.equipments.values():
        for p in equipment.params.values():
            if p.type == "instance":
                p.instance = AppState.equipments[p.instance_name]

    # Instantiate experiments
    for experiment in body.experiments:
        # get the class of the experiment
        _class = getattr(importlib.import_module(experiment.module), experiment.cls)

    # Replace instances with actual equipments
    # TODO accept experiment instance for playlist
    for experiment in AppState.experiments.values():
        for p in experiment.params.values():
            if p.type == "instance":
                p.instance = AppState.equipments[p.instance_name]

    # Initilize the equipment and assign to equipments dict
    for experiment in body.experiments:
        AppState.experiments[experiment.name] = _class(
            params=experiment.params,
        )

    # Run the experiments
    for experiment in body.experiments:
        AppState.run_experiment(experiment.name)
