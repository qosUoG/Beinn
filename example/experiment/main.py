import asyncio
import importlib
import inspect
import json
import os
import pickle
import pkgutil
import pprint

from cnoc.public.equipment import EquipmentABC
from cnoc.public.experiment import ExperimentABC
import traceback
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
import sys

from cnoc.public import params as p


async def main():
    # try:
    #     for names in ["examplelib"]:
    #         pkg = importlib.import_module(names)

    #         for package in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
    #             for [cls, clsT] in inspect.getmembers(
    #                 importlib.import_module(package.name), inspect.isclass
    #             ):
    #                 if (
    #                     (
    #                         not issubclass(clsT, ExperimentABC)
    #                         and not issubclass(clsT, EquipmentABC)
    #                     )
    #                     or clsT is ExperimentABC
    #                     or clsT is EquipmentABC
    #                     or clsT.__module__ != package.name
    #                 ):
    #                     continue

    #                 print(cls, clsT.__module__)
    #                 print(clsT.__module__, package.name)

    #     for package in pkgutil.walk_packages(["."]):
    #         for [cls, clsT] in inspect.getmembers(
    #             importlib.import_module(package.name), inspect.isclass
    #         ):
    #             if (
    #                 (
    #                     not issubclass(clsT, ExperimentABC)
    #                     and not issubclass(clsT, EquipmentABC)
    #                 )
    #                 or clsT is ExperimentABC
    #                 or clsT is EquipmentABC
    #                 or clsT.__module__ != package.name
    #             ):
    #                 continue
    #             print(cls, clsT.__module__)
    #             print(clsT.__module__, package.name)

    # except Exception as e:
    #     traceback.print_exception(e)

    # f = StringIO()

    # with redirect_stdout(f):
    #     with redirect_stderr(sys.stdout):
    #         print("stderr1", file=sys.stderr)
    #         print("stdout1")
    #         print("stderr2", file=sys.stderr)
    #         print("stdout2")

    # print(f.getvalue())
    p.BoolParam(True)


if __name__ == "__main__":
    asyncio.run(main())
    # filename = "./data/ExampleSqlSaver.pickle"

    # with open(filename, "rb") as f:
    #     pprint.pprint(pickle.load(f))

    # Exec mode for multiple statements
