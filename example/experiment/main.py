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
    wow = 1

    async def _print_wow():
        await asyncio.sleep(0.2)
        print(wow)

    async def setwow():
        await asyncio.sleep(0.2)
        wow = 2

    def main():
        task = asyncio.create_task(setwow())
        tt = print_wow()

    def print_wow():
        asyncio.create_task(_print_wow())

    async def mmain():
        main()

    asyncio.run(mmain())

    print(wow)

    sleep(2)
    print(wow)

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
