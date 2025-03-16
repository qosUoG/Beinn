import importlib
from fastapi import APIRouter
from pydantic import BaseModel


from qoslablib.runtime import EquipmentABC

from qoslablib.params import ParamModels, Params2ParamModels, ParamModels2Params


from ._eeshared import getAvailableEEs, populateParam


from ..lib.state import AppState


router = APIRouter()


class AvailableEquipmentsPayload(BaseModel):
    prefixes: list[str]


@router.post("/equipment/available_equipments")
async def available_equipments(payload: AvailableEquipmentsPayload):
    return getAvailableEEs(EquipmentABC, payload.prefixes)


class CreateEquipmentPayload(BaseModel):
    id: str
    module: str
    cls: str


@router.post("/equipment/create")
async def create_equipment(payload: CreateEquipmentPayload):
    AppState.createEquipment(
        payload.id, getattr(importlib.import_module(payload.module), payload.cls)
    )


class RemoveEquipmentPayload(BaseModel):
    id: str


@router.post("/equipment/remove")
async def remove_equipment(payload: RemoveEquipmentPayload):
    AppState.removeEquipment(payload.id)


class GetParamsPayload(BaseModel):
    id: str


@router.post("/equipment/get_params")
async def get_params(payload: GetParamsPayload):
    return Params2ParamModels(AppState.getEquipmentParams(payload.id))


class SetParamsPayload(BaseModel):
    params: ParamModels
    # Equipment id
    id: str


@router.post("/equipment/set_params")
async def set_params(payload: SetParamsPayload):
    params = ParamModels2Params(payload.params)
    for [param_name, param] in params.items():
        params[param_name] = populateParam(param)

    AppState.setEquipmentParams(params)
