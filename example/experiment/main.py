import asyncio
from dataclasses import dataclass
import dataclasses
import importlib
import inspect
import json
import pkgutil
from threading import Event, Lock
from time import sleep
import types
from typing import Any

from qoslablib.extensions.chart import XYPlotConfig


if __name__ == "__main__":
    config = XYPlotConfig(
        title="wow", type="XYPlot", x_axis="xxx", y_axis="yyy", y_names=["temperature"]
    )
    print(dataclasses.asdict(config))

    # def inside():
    #     warnings.filterwarnings("error")

    # try:
    #     inside()
    #     warnings.warn("This is a warning")
    # except Warning:
    #     print("This is a exception")

    # print(getattr(examplelib.ExampleDriver.ExampleEquipment, "equipment_params"))
    # for [p, module] in inspect.getmembers(
    #     importlib.import_module("examplelib.ExampleDriver")
    # ):
    #     if not p.startswith("__"):
    #         print(p, module)
