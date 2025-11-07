from dataclasses import dataclass


import random
from typing import Callable, override


import time


from cnoc import charts, p, Saver, ExperimentABC, Manager, ExperimentEnded

from examplelib.ExampleDriver import ExampleEquipment
import pandas as pd


@dataclass
class CompositeParamsType:
    compstrparam = p.str()
    compfloatparam = p.float(suffix="W")

    compintparam = p.int()
    compboolparam = p.boolean(False)
    compselectstrparam = p.select.str(["option1", "option2", "option3"])

    compselectintparam = p.select.int([1, 2, 3])
    compselectfloatparam = p.select.float([1.1, 2.2, 3.3])
    compinstanceequipmentparam = p.equipment[ExampleEquipment].instance()


class ExampleExperiment(ExperimentABC):
    @dataclass
    class ParamsType:
        strparam = p.str()
        floatparam = p.float(suffix="W")
        intparam = p.int()
        boolparam = p.boolean(False)
        selectstrparam = p.select.str(["option1", "option2", "option3"])
        selectintparam = p.select.int([1, 2, 3], 1)
        selectfloatparam = p.select.float([1.1, 2.2, 3.3])
        composite = p.composite(CompositeParamsType)

    def __init__(self):
        # The name of the experiment assigned during runtime would be made accessible.
        # You would need it to pass to the createChart and createSqlSaver methods

        super().__init__()

        # This should be all of the __init__ code. For instantiation of params from the final params list, or turning on equipment, initializing equipment etc, define in the start method

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
            y_names=["temperature"],
            mode="append",
        )
        manager.createChart(self.scatter_plot1)
        self.scatter_plot2: charts.Scatter = charts.Scatter(
            title="Example Scatter Plot2",
            x_axis="index",
            x_name="index",
            y_axis="C",
            y_names=["temperature"],
            mode="append",
        )
        manager.createChart(self.scatter_plot2)
        self.saver = Saver("data.h5", self.params)

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
        value = random.random()
        self.scatter_plot1.plot(
            {
                "index": index,
                "temperature": value,
            }
        )
        self.saver.save(pd.DataFrame({"index": [index], "temperature": [value]}))
        print("experiment loop", index, flush=True)

        if index >= 9:
            raise ExperimentEnded

    @override
    def cleanup(self):
        # define code here for clean up, for example switching off some equipment etc
        pass
