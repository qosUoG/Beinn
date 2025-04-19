from fastapi import APIRouter
from pydantic import BaseModel


from cnoc.runtime import EquipmentABC

from cnoc.params import ParamModels, Params2ParamModels, ParamModels2Params

from ..lib.utils.result import applicationError, ok


from ._eeshared import getAvailableEEs, populateParam


from ..lib.settings.state import AppState


router = APIRouter()


class AvailableEquipmentsPayload(BaseModel):
    prefixes: list[str]


@router.post("/equipment/available_equipments")
async def available_equipments(payload: AvailableEquipmentsPayload):
    try:
        return ok(getAvailableEEs(EquipmentABC, payload.prefixes))
    except Exception as e:
        return applicationError(f"error in /equipment/create: {e}")


class CreateEquipmentPayload(BaseModel):
    id: str
    module: str
    cls: str


@router.post("/equipment/create")
async def create_equipment(payload: CreateEquipmentPayload):
    try:
        AppState.createEquipment(payload.id, payload.module, payload.cls)
        return ok()
    except Exception as e:
        return applicationError(f"error in /equipment/create: {e}")


class RemoveEquipmentPayload(BaseModel):
    id: str


@router.post("/equipment/remove")
async def remove_equipment(payload: RemoveEquipmentPayload):
    try:
        AppState.removeEquipment(payload.id)
        return ok()
    except Exception as e:
        return applicationError(f"error in /equipment/remove: {e}")


class GetParamsPayload(BaseModel):
    id: str


@router.post("/equipment/get_params")
async def get_params(payload: GetParamsPayload):
    try:
        return ok(Params2ParamModels(AppState.getEquipmentParams(payload.id)))
    except Exception as e:
        return applicationError(f"error in /equipment/get_params: {e}")


class SetParamsPayload(BaseModel):
    params: ParamModels
    # Equipment id
    id: str


@router.post("/equipment/set_params")
async def set_params(payload: SetParamsPayload):
    try:
        params = ParamModels2Params(payload.params)
        for [param_name, param] in params.items():
            params[param_name] = populateParam(param)

        AppState.setEquipmentParams(payload.id, params)
        return ok()
    except Exception as e:
        return applicationError(f"error in /equipment/set_params: {e}")
