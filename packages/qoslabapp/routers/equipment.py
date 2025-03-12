import importlib
from fastapi import APIRouter
from pydantic import BaseModel


from qoslablib.runtime import EquipmentABC

from qoslablib.params import ParamModels, Params2ParamModels, ParamModels2Params


from .eeshared import getAvailableEEs, populateParam


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
    _class = getattr(importlib.import_module(payload.module), payload.cls)
    AppState.equipments[payload.id] = _class()


class GetParamsPayload(BaseModel):
    id: str


@router.post("/equipment/get_params")
async def get_params(payload: GetParamsPayload):
    res = Params2ParamModels(AppState.equipments[payload.id].params)

    import pprint

    pprint(res)
    return res


class SetParamsPayload(BaseModel):
    params: ParamModels
    # Equipment id
    id: str


@router.post("/equipment/set_params")
async def set_params(payload: SetParamsPayload):
    params = ParamModels2Params(payload.params)
    for [param_name, param] in params.items():
        AppState.equipments[payload.id].params[param_name] = populateParam(param)
