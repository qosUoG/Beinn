from fastapi import APIRouter
import os

from pydantic import BaseModel
from qoslabpy import labtype as l
from lib.state import AppState
from lib.utils import importFromStr


router = APIRouter()


class Path(BaseModel):
    path: str


@router.post("/workspace/set_directory")
async def set_directory(body: Path):
    """
    Set and Reads the content of a directory
    """
    print(body)
    path = body.path
    AppState.project["path"] = path

    res = []
    with os.scandir(path) as it:
        for entry in it:
            if not entry.name.startswith(".") and entry.is_file():
                res.append(entry.name)

    return res


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
