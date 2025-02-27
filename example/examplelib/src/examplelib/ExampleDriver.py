from pydantic import BaseModel
from qoslab_lib import params as p


class ExampleEquipment:
    class ParamsType(BaseModel):
        strparam: p.StrParam
        floatparam: p.FloatParam
        intparam: p.IntParam
        boolparam: p.BoolParam
        selectstrparam: p.SelectStrParam
        selectintparam: p.SelectIntParam
        selectfloatparam: p.SelectFloatParam

    params: ParamsType = {
        "strparam": p.str_param(),
        "floatparam": p.float_param(suffix="W"),
        "intparam": p.int_param(),
        "boolparam": p.bool_param(False),
        "selectstrparam": p.select_str_param(["option1", "option2", "option3"]),
        "selectintparam": p.select_int_param([1, 2, 3]),
        "selectfloatparam": p.select_float_param([1.1, 2.2, 3.3]),
    }

    def __init__(self, params: ParamsType):
        self.params = params
        # Other initialisation code below

    def square(self, num: int):
        return num * num
