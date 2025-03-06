from pydantic import BaseModel

from qoslablib.params import AllParamTypes


class Experiment(BaseModel):
    name: str
    module: str
    cls: str
    params: dict[str, AllParamTypes]


class Equipment(BaseModel):
    name: str
    module: str
    cls: str
    params: dict[str, AllParamTypes]
