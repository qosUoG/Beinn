from dataclasses import dataclass


import random
from typing import Callable, TypedDict, override


import time


from cnoc import charts, p, Saver, ExperimentABC, Manager, ExperimentEnded, P

from examplelib.ExampleDriver import ExampleEquipment
import numpy as np


@dataclass
class CompositeParamsType:
    compstrparam: P.Str = p.str()
    compfloatparam: P.Float = p.float(suffix="W")
    compintparam: P.Int = p.int()
    compboolparam: P.Bool = p.boolean(False)
    compselectstrparam: P.Select.Str = p.select.str(["option1", "option2", "option3"])
    compselectintparam: P.Select.Int = p.select.int([1, 2, 3])
    compselectfloatparam: P.Select.Float = p.select.float([1.1, 2.2, 3.3])
    compinstanceequipmentparam: P.Equipment[ExampleEquipment] = p.equipment()


@dataclass
class Params:
    strparam: P.Str = p.str("wowow")
    floatparam: P.Float = p.float(suffix="W")
    intparam: P.Int = p.int()
    boolparam: P.Bool = p.boolean(False)
    selectstrparam: P.Select.Str = p.select.str(["option1", "option2", "option3"])
    selectintparam: P.Select.Int = p.select.int([1, 2, 3], 1)
    selectfloatparam: P.Select.Float = p.select.float([1.1, 2.2, 3.3])
    composite: CompositeParamsType = p.composite(CompositeParamsType)


class SaverRowType(TypedDict):
    index: list[int]
    t1: list[float]
    t2: list[float]
    t3: np.typing.NDArray[np.float64]
    i2: list[int]


class ExampleExperiment(ExperimentABC[Params]):
    params = Params()

    @override
    def start(self, manager: Manager):
        # # You may interact with the equipment here to do initialization
        # self.params["instance_equipment_param"].instance.echo("hellow world")
        # self.params["instance_equipment_param"].instance.power = 10

        # # You would instantiate ranges, or other derived values for use in loop from params here as well
        # self.inputs = numpy.arange(self.params["intparam"].value)

        # # # After the params, instantiate charts and sql savers as needed
        self.scatter_plot1: charts.Scatter = charts.Scatter(
            title="Example Scatter Plot1",
            x_axis="index",
            x_name="index",
            y_axis="C",
            y_names=["t1", "t2", "t3"],
            mode="append",
        )
        manager.createChart(self.scatter_plot1)
        self.scatter_plot2: charts.Scatter = charts.Scatter(
            title="Example Scatter Plot2",
            x_axis="index",
            x_name="index",
            y_axis="C",
            y_names=["t1", "t2", "t3"],
            mode="append",
        )
        manager.createChart(self.scatter_plot2)
        self.saver = Saver[SaverRowType]("temp_data", self.params, SaverRowType)

        manager.createSaver(self.saver)

        # self.xyplot2: XY = manager.createChart(
        #     XY,
        #     XY.kwargs(
        #         title="Another XY Plot",
        #         x_name="indexxxx",
        #         y_names=["temperature"],
        #     ),
        # )

        # self.saver: XYFloatSaver = manager.createSaver(
        #     XYFloatSaver,
        #     XYFloatSaver.kwargs(title="ExampleSqlSaver", y_names=["temperature"]),
        # )

        manager.expected_loop_count = 10

    @override
    def loop(self, index: int, shouldStop: Callable[[], bool]):
        # # In each loop, perform measurements

        # # set the power of the equipment
        # self.params["instance_equipment_param"].instance.power = self.inputs[index]
        # # Measure the "temp"
        # temp = self.params["instance_equipment_param"].instance.measureTemp()

        # # Then plot and save the data
        # # Since python's typing capability is limited, you would need to make sure you did write the correct keys yourself
        # self.xyplot.plot({"index": index, "temperature": temp})
        # self.saver.save({"index": index, "temperature": temp})

        # # This is here just to not make everything happening too quickly
        time.sleep(0.5)

        # Raise an exception such that qoslapapp knows experiment is ended
        # print(f"loop: {index}")
        v1 = random.random()
        v2 = random.random()
        v3 = random.random()
        self.scatter_plot1.plot(
            {
                "index": [index],
                "t1": [v1],
                "t2": [v2],
                "t3": [v3],
            }
        )
        self.saver.save(
            {
                "index": [index],
                "t1": [v1],
                "t2": [v2],
                "t3": np.array([v3]),
                "i2": [index * 2],
            }
        )
        print("experiment loop", index)

        if index >= 9:
            raise ExperimentEnded

    @override
    def cleanup(self):
        # define code here for clean up, for example switching off some equipment etc
        pass
