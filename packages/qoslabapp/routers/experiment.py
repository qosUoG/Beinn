from fastapi import APIRouter, WebSocket

from pydantic import BaseModel


from qoslablib.runtime import ExperimentABC

from qoslablib.params import ParamModels, ParamModels2Params, Params2ParamModels

from ._eeshared import getAvailableEEs, populateParam

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
    AppState.createExperiment(payload.id, payload.module, payload.cls)


class RemoveExperimentPayload(BaseModel):
    id: str


@router.post("/experiment/remove")
async def remove_experiment(payload: RemoveExperimentPayload):
    AppState.removeExperiment(payload.id)


class GetParamsPayload(BaseModel):
    id: str


@router.post("/experiment/get_params")
async def get_params(payload: GetParamsPayload):
    return Params2ParamModels(AppState.getExperimentParams(payload.id))


class SetParamsPayload(BaseModel):
    params: ParamModels
    # Experiment id
    id: str


@router.post("/experiment/set_params")
async def set_params(payload: SetParamsPayload):
    params = ParamModels2Params(payload.params)
    for [param_name, param] in params.items():
        params[param_name] = populateParam(param)

    AppState.setExperimentParams(payload.id, params)


# Websockets implemented with non async as the underlying event used is Threading ones
@router.websocket("/experiment/{experiment_id}/loop_count")
def getStreamingLoopCount(ws: WebSocket, experiment_id: str):
    ws.accept()
    while True:
        for loop_count in AppState.getStreamingLoopCount(experiment_id)():
            ws.send_text("{" + f"loop_count: {loop_count}" + "}")


class StartExperimentPayload(BaseModel):
    id: str


@router.post("/experiment/start_experiment")
async def start_experiment(payload: StartExperimentPayload):
    # Run the experiments
    AppState.startExperiment(payload.id)
