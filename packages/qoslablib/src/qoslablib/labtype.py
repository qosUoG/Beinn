from pydantic import BaseModel

from qoslablib.params import AllParamTypes


class ExperimentModule(BaseModel):
    name: str
    module: str
    cls: str
    params: dict[str, AllParamTypes]


class EquipmentModule(BaseModel):
    name: str
    module: str
    cls: str
    params: dict[str, AllParamTypes]
