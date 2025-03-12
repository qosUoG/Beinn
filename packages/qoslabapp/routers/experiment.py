import importlib
from fastapi import APIRouter
from pydantic import BaseModel


from qoslablib.runtime import ExperimentABC

from qoslablib.params import ParamModels

from .eeshared import getAvailableEEs, populateParam


from ..lib.state import AppState


router = APIRouter()


class AvailableExperimentsPayload(BaseModel):
    prefixes: list[str]


@router.post("/experiment/available_experiments")
async def available_experiments(payload: AvailableExperimentsPayload):
    return getAvailableEEs(ExperimentABC, payload.prefixes)


class CreateExperimentPayload(BaseModel):
    id: str
    module: str
    cls: str


@router.post("/experiment/create")
async def create_experiment(payload: CreateExperimentPayload):
    _class = getattr(importlib.import_module(payload.module), payload.cls)
    AppState.experiments[payload.id] = _class()


class GetParamsPayload(BaseModel):
    id: str


@router.post("/experiment/get_params")
async def get_params(payload: GetParamsPayload):
    return AppState.experiments[payload.id].params


class SetParamPayload(BaseModel):
    params: ParamModels
    # Experiment id
    id: str


@router.post("/experiment/set_params")
async def set_params(payload: SetParamPayload):
    for [param_name, param] in payload.params.items():
        AppState.experiments[payload.id].params[param_name] = populateParam(param)


class StartExperimentPayload(BaseModel):
    experiment_name: str


@router.post("/experiment/start_experiment")
async def start_experiment(payload: StartExperimentPayload):
    # Run the experiments
    AppState.run_experiment(payload.experiment_name)
