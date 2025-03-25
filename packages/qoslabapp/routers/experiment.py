import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pydantic import BaseModel


from qoslablib.runtime import ExperimentABC

from qoslablib.params import ParamModels, ParamModels2Params, Params2ParamModels

from ._eeshared import getAvailableEEs, populateParam

from ..lib.settings.state import AppState


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
@router.websocket("/experiment/{experiment_id}/events")
async def subscribeExperimentEvents(ws: WebSocket, experiment_id: str):
    await ws.accept()

    (getFn, unsubscribe) = AppState.subscribeExperimentMessage(experiment_id, ws)
    try:
        while True:
            await ws.send_text(await getFn())

    except WebSocketDisconnect:
        unsubscribe()
    except asyncio.QueueShutDown:
        await ws.close()
        unsubscribe()


class controlExperimentPayload(BaseModel):
    id: str


@router.post("/experiment/start")
async def start_experiment(payload: controlExperimentPayload):
    # Run the experiments
    AppState.startExperiment(payload.id)


@router.post("/experiment/pause")
async def pause_experiment(payload: controlExperimentPayload):
    # Run the experiments
    AppState.pauseExperiment_sync(payload.id)


@router.post("/experiment/continue")
async def continue_experiment(payload: controlExperimentPayload):
    # Run the experiments
    AppState.continueExperiment(payload.id)


@router.post("/experiment/stop")
async def stop_experiment(payload: controlExperimentPayload):
    # Run the experiments
    AppState.stopExperiment_sync(payload.id)
