import importlib


def main():
    print("Hello from experiment!")


if __name__ == "__main__":
    import examplelib.ExampleDriver
    import inspect

    print(importlib.util.find_spec("msvcrt"))

    if importlib.util.find_spec("msvcrt"):
        print("wtf")

    import asyncio.windows_utils

    # print(getattr(examplelib.ExampleDriver.ExampleEquipment, "equipment_params"))
    # for [p, module] in inspect.getmembers(
    #     importlib.import_module("examplelib.ExampleDriver")
    # ):
    #     if not p.startswith("__"):
    #         print(p, module)
