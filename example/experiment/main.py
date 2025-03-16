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

    class A:
        x = 1

        @classmethod
        def getx(cls):
            return cls.x

        def echo(self, value: str):
            return value

        pass

    @dataclass
    class B:
        a = A()
        _lock = Lock()

        def __getattr__(self, key: str):
            attr = getattr(self.a, key)
            if callable(attr):

                def wrap(*args, **kwargs):
                    with self._lock:
                        return attr(*args, **kwargs)

                return wrap

            return attr

        def __setattr__(self, key: str, value: Any):
            return setattr(self.a, key, value)

    b = B()

    b.x = 2

    print(b.x)
    print(b.a.x)
    print(b.echo)
    print(b.echo("hi"))
    print(b.a.echo)
    print(b.a.echo("hhhi"))

    b.sth = "wow"
    print(b.sth)
    print(b.a.sth)
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
