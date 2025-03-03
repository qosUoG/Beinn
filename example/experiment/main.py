import importlib
import inspect
import pkgutil

import examplelib

# import examplelib.ExampleDriver
import pprint
import msvcrt

import examplelib.ExampleDriver


if __name__ == "__main__":
    importlib.__import__("msvcrt")
    if hasattr(examplelib.ExampleDriver, "params"):
        print("has")
    # names = set()
    # for [name, _] in inspect.getmodule(examplelib.ExampleDriver):
    # count = 1
    # start = 800
    # for _, name, _ in pkgutil.walk_packages():
    #     count += 1
    #     if count >= start:
    #         names.add(name)

    #     if count > start + 100:
    #         break

    # pprint.pprint(sorted(names))
