import importlib
from fastapi import APIRouter
from pydantic import BaseModel

from lib.state import AppState
from lib.utils import importFromStr
from qoslablib import labtype as l


router = APIRouter()


class GetParamPayload(BaseModel):
    module: str
    cls: str


@router.post("/equipment/get_params")
async def get_params(payload: GetParamPayload):
    return getattr(
        getattr(payload.cls, importlib.import_module(payload.module)),
        "equipment_params",
    )


class LoadEquipmentPayload(BaseModel):
    equipments: list[l.Equipment]


# Equipment Endpoints
@router.post("/equipment/load")
async def loadEquipment(payload: LoadEquipmentPayload):
    AppState.equipments.clear()
    for equipment in payload.equipments:
        with open(equipment.path, mode="r", encoding="utf-8") as raw:
            # Read the definition code from the source file
            [module, classname] = importFromStr(raw.read())
            _class = getattr(module, classname)
            # Initilize the equipment and assign to equipments dict
            AppState.equipments[equipment.name] = _class(equipment.params)
            # Loop and assign instances to each param
            for equipment in AppState.equipments.values():
                for p in equipment.params.values():
                    if p.type == "instance":
                        p.instance = AppState.equipments[p.instance_name]
    import pprint

    pprint.pp(AppState.equipments)
