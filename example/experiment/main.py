import importlib
import pkgutil


def main():
    print("Hello from experiment!")


if __name__ == "__main__":
    import examplelib.ExampleDriver
    import inspect
    import warnings

    importlib.util.find_spec("fastapi_cli.utils.cli")

    for package in pkgutil.iter_modules():
        if "abcde" in package.name:
            print(package.name)

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
