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
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
import sys


async def main():
    # try:
    #     for package in pkgutil.walk_packages():
    #         if not package.name.startswith("lib"):
    #             continue
    #         for [cls, clsT] in inspect.getmembers(
    #             importlib.import_module(package.name), inspect.isclass
    #         ):
    #             if (
    #                 not issubclass(clsT, ExperimentABC)
    #                 or clsT is ExperimentABC
    #                 or clsT is EquipmentABC
    #             ):
    #                 continue

    #             print(cls)

    # except Exception as e:
    #     if package.name.startswith("lib"):
    #         print(package.name)
    #         print(e)
    #         traceback.print_exception(e)

    f = StringIO()

    with redirect_stdout(f):
        with redirect_stderr(sys.stdout):
            print("stderr1", file=sys.stderr)
            print("stdout1")
            print("stderr2", file=sys.stderr)
            print("stdout2")

    print(f.getvalue())


if __name__ == "__main__":
    asyncio.run(main())
    # filename = "./data/ExampleSqlSaver.pickle"

    # with open(filename, "rb") as f:
    #     pprint.pprint(pickle.load(f))

    # Exec mode for multiple statements
