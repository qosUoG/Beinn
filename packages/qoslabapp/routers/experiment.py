import importlib
from fastapi import APIRouter
from pydantic import BaseModel

from ..lib.state import AppState
from qoslablib import labtype as l
from ..lib.utils import importFromStr


router = APIRouter()


class GetParamPayload(BaseModel):
    module: str
    cls: str


@router.post("/experiment/get_params")
async def get_params(payload: GetParamPayload):
    return getattr(
        getattr(importlib.import_module(payload.module), payload.cls),
        "experiment_params",
    )


class StartExperimentsPayload(BaseModel):
    equipments: list[l.Equipment]
    experiments: list[l.Experiment]


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
        # Read the definition code from the source file
        _class = getattr(importlib.import_module(experiment.module), experiment.cls)

    # Replace instances with actual equipments
    # TODO accept experiment instance for playlist
    for experiment in AppState.experiments.values():
        for p in experiment.params.values():
            if p.type == "instance":
                p.instance = AppState.equipments[p.instance_name]

    # Initilize the equipment and assign to equipments dict
    for experiment in body.experiments:
        AppState.experiments[experiment.name] = _class(experiment.params)
