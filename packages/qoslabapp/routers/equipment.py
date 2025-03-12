import importlib
from fastapi import APIRouter
from pydantic import BaseModel

from qoslablib.params import Params
from qoslablib.runtime import EquipmentABC

from .eeshared import getAvailableEEs, populateParam


from ..lib.state import AppState


router = APIRouter()


class AvailableEquipmentsPayload(BaseModel):
    names: list[str]


@router.post("/equipment/available_equipments")
async def available_equipments(payload: AvailableEquipmentsPayload):
    return getAvailableEEs(EquipmentABC, payload.names)


class CreateEquipmentPayload(BaseModel):
    name: str
    module: str
    cls: str


@router.post("/equipment/create")
async def create_equipment(payload: CreateEquipmentPayload):
    _class = getattr(importlib.import_module(payload.module), payload.cls)
    AppState.equipments[payload.name] = _class()


class GetParamsPayload(BaseModel):
    name: str


@router.post("/equipment/get_params")
async def get_params(payload: GetParamsPayload):
    return AppState.equipments[payload.name].params


class SetParamPayload(BaseModel):
    params: Params
    # Equipment name
    name: str
    # param name


@router.post("/equipment/set_params")
async def set_params(payload: SetParamPayload):
    for [param_name, param] in payload.params.items():
        AppState.equipments[payload.name].params[param_name] = populateParam(param)
