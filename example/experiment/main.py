import asyncio
from dataclasses import dataclass
import importlib
import inspect
import pkgutil
from threading import Event, Lock
from time import sleep
import types
from typing import Any


async def main():
    e = Event()

    async def priiint():
        print("start wait")

        await asyncio.to_thread(e.wait)
        print("end wait")

    async def sleeeep():
        print("start sleep")
        await asyncio.sleep(2)
        print("end sleep")
        e.set()

    await asyncio.gather(sleeeep(), priiint())


if __name__ == "__main__":
    asyncio.run(main())

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
