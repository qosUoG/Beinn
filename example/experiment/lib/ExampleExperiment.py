from dataclasses import dataclass
from typing import TypedDict

from click import ParamType
from qoslablib import params as p, exceptions as e, runtime as r
import time

from qoslablib.chart import XYPlot
from qoslablib.saver import XYSqlSaver
from examplelib.ExampleDriver import ExampleEquipment


@dataclass
class ExamplExperiment(r.ExperimentABC):
    class ParamsType(TypedDict):
        strparam: p.StrParam
        floatparam: p.FloatParam
        intparam: p.IntParam
        boolparam: p.BoolParam
        selectstrparam: p.SelectStrParam
        selectintparam: p.SelectIntParam
        selectfloatparam: p.SelectFloatParam
        instance_equipment_param: p.InstanceParam[ExampleEquipment]

    params: ParamType

    def __init__(self, holder: r.HoldersABC):
        # Step 1. Call Super
        # Currently it does nothing, this is just to ensure foward compatability
        super.__init__(self)

        self.params: ExamplExperiment.ParamsType = {
            "strparam": p.str_param(),
            "floatparam": p.float_param(suffix="W"),
            "intparam": p.int_param(),
            "boolparam": p.bool_param(False),
            "selectstrparam": p.select_str_param(["option1", "option2", "option3"]),
            "selectintparam": p.select_int_param([1, 2, 3]),
            "selectfloatparam": p.select_float_param([1.1, 2.2, 3.3]),
            "instance_equipment_param": p.instance_equipment_param[ExampleEquipment](),
        }

        # # After the params list, instantiate charts and sql savers as needed
        self.xyplot = holder.createChart[XYPlot](
            XYPlot,
            XYPlot.kwargs(
                title="Example XY Plot",
                x_name="index",
                y_names=["amplitude"],
            ),
        )

        self.saver = holder.createSqlSaver[XYSqlSaver](
            XYSqlSaver,
            XYSqlSaver.kwargs(
                title="ExampleSqlSaver", x_name="index", y_names=["amplitude"]
            ),
        )

        # This should be all of the __init__ code. For instantiation of params from the final params list, or turning on equipment, initializing equipment etc, define in the initialization method

    def initialize(self):
        import pprint

        pprint.pprint(self.params)

        self.params["instance_equipment_param"].instance.echo("hellow world")
        self.params["instance_equipment_param"].instance.amplitude = 10

    def loop(self, index: int):
        if index >= 10:
            raise e.ExperimentEnded
        print(self.params["instance_equipment_param"].instance.amplitude(index))
        time.sleep(1)
