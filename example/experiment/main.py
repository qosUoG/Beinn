import asyncio
import datetime
import importlib
import inspect
import json
import os
import pickle
import pkgutil
import pprint
import threading
import time
import timeit


from cnoc.public.equipment import EquipmentABC
from cnoc.public.experiment import ExperimentABC
import traceback
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
import sys

from numpy import dtype
import pandas as pd
import lib

from cnoc.public import params as p

from cnoc.public import saver


async def main():
    store = saver.Reader("data.h5")
    print(store.keys())
    print(store.values())
    print(store.items())

    # store = pd.HDFStore("data.h5")
    # print(store.keys())
    # store.close()

    # without_time = print(timeit.timeit(withoutJson, number=10000))

    # print(with_time)
    # print(without_time)

    # store.put("data", json.dumps({"hi": {"hi": "hi"}}), format="table")
    # df2 = pd.DataFrame([[5, 6], [7, 8]], columns=["A", "B"])
    # store.append(
    #     "data",
    #     json.dumps({"bye": {"bye": "bye"}})),
    # )
    # print(store.get("data"))
    # store.close()

    # print(
    #     time.strftime("%Y/%m/%d %H:%M:%S UTC%z", time.localtime()),
    # )


if __name__ == "__main__":
    asyncio.run(main())
    # filename = "./data/ExampleSqlSaver.pickle"

    # with open(filename, "rb") as f:
    #     pprint.pprint(pickle.load(f))

    # Exec mode for multiple statements
