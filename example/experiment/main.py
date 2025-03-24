import array
import asyncio
from dataclasses import dataclass
import dataclasses
import importlib
import inspect
import json
import pkgutil

from threading import Event
from time import sleep
import types
from typing import Any

from qoslablib.extensions.chart import XYPlotConfig
from qoslablib.extensions.saver import KVSqlSaverConfig


if __name__ == "__main__":

    def xxx(i: int):
        print("xxx" + str(i))

    callback = lambda i: xxx(i)

    callback(1)

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
