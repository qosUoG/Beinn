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

    def main():
        done_event = Event()
        task = asyncio.create_task(wait())
        task.add_done_callback(lambda: done_event.set())
        done_event.wait()
        result = task.result()
        print("done" + result)

    async def wait():
        await asyncio.sleep(1)
        return 1

    async def mmain():
        main()

    asyncio.run(mmain())

    print("hi")

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
