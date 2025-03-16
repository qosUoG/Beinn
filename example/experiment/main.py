import asyncio
from dataclasses import dataclass
import importlib
import inspect
import pkgutil
from threading import Event, Lock
import types
from typing import Any


def main():
    print("Hello from experiment!")


if __name__ == "__main__":
    x = 1
    print(f"{{loop_count: {x}\}}\n\n")
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
