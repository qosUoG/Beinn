import asyncio
import importlib
import inspect
import os
import pickle
import pkgutil
import pprint

from cnoc.equipment import EquipmentABC
from cnoc.experiment import ExperimentABC
import traceback


async def main():
    try:
        for package in pkgutil.walk_packages():
            if not package.name.startswith("lib"):
                continue
            for [cls, clsT] in inspect.getmembers(
                importlib.import_module(package.name), inspect.isclass
            ):
                if (
                    not issubclass(clsT, ExperimentABC)
                    or clsT is ExperimentABC
                    or clsT is EquipmentABC
                ):
                    continue

                print(cls)

    except Exception as e:
        if package.name.startswith("lib"):
            print(package.name)
            print(e)
            traceback.print_exception(e)


if __name__ == "__main__":
    asyncio.run(main())
    # filename = "./data/ExampleSqlSaver.pickle"

    # with open(filename, "rb") as f:
    #     pprint.pprint(pickle.load(f))

    # Exec mode for multiple statements
