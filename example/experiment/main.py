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

    class EquipmentProxy:
        # Threading.Lock for thread safety access of Equipment

        def __init__(self):
            super().__setattr__("_lock", Lock())
            super().__setattr__("_equipment", 1)

        # For Type safety
        @property
        def params(self):
            with super()._lock:
                return super()._equipment

        @params.setter
        def params(self, value: int):
            with super()._lock:
                super()._equipment = value

        # Proxy to all underlying parameters
        def __getattr__(self, key: str):
            with super()._lock:
                attr = getattr(super()._equipment, key)
                if callable(attr):

                    def wrap(*args, **kwargs):
                        with super()._lock:
                            return attr(*args, **kwargs)

                    return wrap

                return attr

        def __setattr__(self, key: str, value: Any):
            with super()._lock:
                setattr(super()._equipment, key, value)

    e = EquipmentProxy()

    print(e.params)

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
