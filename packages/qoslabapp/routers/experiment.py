import importlib
from fastapi import APIRouter
from pydantic import BaseModel

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


# class StartExperimentPayload(BaseModel):
#     path: str
#     methodname: str
#     params: dict[str, AllParamTypes]


# @router.post("/experiment/start")
# async def startExperiment(payload: StartExperimentPayload):
#     """
#     Start Experiment
#     """
#     with open(payload.path, mode="r", encoding="utf-8") as raw:
#         # Read the definition code from the source file
#         exec(raw.read())
#         # Create the experiment in a separate thread
#         exec(
#             f"AppState.experiment_threads['{payload.methodname}'] = Thread(target={payload.methodname}, args={payload.params})"
#         )
#         # Start running the experiment
#         exec(f"AppState.experiment_threads['{payload.methodname}'].start()")
