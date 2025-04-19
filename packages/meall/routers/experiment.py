import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pydantic import BaseModel


from cnoc.runtime import ExperimentABC

from cnoc.params import ParamModels, ParamModels2Params, Params2ParamModels

from ..lib.utils.result import applicationError, ok

from ._eeshared import getAvailableEEs, populateParam

from ..lib.settings.state import AppState


router = APIRouter()


class AvailableExperimentsPayload(BaseModel):
    prefixes: list[str]


@router.post("/experiment/available_experiments")
async def available_experiments(payload: AvailableExperimentsPayload):
    try:
        return ok(getAvailableEEs(ExperimentABC, payload.prefixes))
    except Exception as e:
        return applicationError(f"error in /experiment/available_experiments: {e}")


class CreateExperimentPayload(BaseModel):
    id: str
    module: str
    cls: str


@router.post("/experiment/create")
async def create_experiment(payload: CreateExperimentPayload):
    try:
        AppState.createExperiment(payload.id, payload.module, payload.cls)
        return ok()
    except Exception as e:
        return applicationError(f"error in /experiment/create: {e}")


class RemoveExperimentPayload(BaseModel):
    id: str


@router.post("/experiment/remove")
async def remove_experiment(payload: RemoveExperimentPayload):
    try:
        AppState.removeExperiment(payload.id)
        return ok()
    except Exception as e:
        return applicationError(f"error in /experiment/remove: {e}")


class GetParamsPayload(BaseModel):
    id: str


@router.post("/experiment/get_params")
async def get_params(payload: GetParamsPayload):
    try:
        return ok(Params2ParamModels(AppState.getExperimentParams(payload.id)))
    except Exception as e:
        return applicationError(f"error in/experiment/get_params: {e}")


class SetParamsPayload(BaseModel):
    params: ParamModels
    # Experiment id
    id: str


@router.post("/experiment/set_params")
async def set_params(payload: SetParamsPayload):
    try:
        params = ParamModels2Params(payload.params)
        for [param_name, param] in params.items():
            params[param_name] = populateParam(param)

        AppState.setExperimentParams(payload.id, params)
        return ok()
    except Exception as e:
        return applicationError(f"error in /experiment/set_params: {e}")


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
    try:
        # Run the experiments
        AppState.startExperiment(payload.id)
        return ok()
    except Exception as e:
        return applicationError(f"error in /experiment/start: {e}")


@router.post("/experiment/pause")
async def pause_experiment(payload: controlExperimentPayload):
    # Run the experiments
    try:
        AppState.pauseExperiment_sync(payload.id)
        return ok()
    except Exception as e:
        return applicationError(f"error in /experiment/pause: {e}")


@router.post("/experiment/continue")
async def continue_experiment(payload: controlExperimentPayload):
    # Run the experiments
    try:
        AppState.continueExperiment(payload.id)
        return ok()
    except Exception as e:
        return applicationError(f"error in /experiment/continue: {e}")


@router.post("/experiment/stop")
async def stop_experiment(payload: controlExperimentPayload):
    # Run the experiments
    try:
        AppState.stopExperiment_async(payload.id)
        return ok()
    except Exception as e:
        return applicationError(f"error in /experiment/stop: {e}")
