import array
import asyncio
from dataclasses import dataclass
import dataclasses
import importlib
import inspect
import json
import math
import pkgutil

from threading import Event
from time import sleep
import time
import types
from typing import Any

import aiosqlite
from qoslablib.extensions.chart import XYPlotConfig
from qoslablib.extensions.saver import KVSqlSaverConfig


if __name__ == "__main__":

    async def main():
        _sqlite3_connection = await aiosqlite.connect("data.db")
        _sqlite3_cursor = await _sqlite3_connection.cursor()
        time_stamp = math.floor(time.time() * 1000)

        print("hi")
        await _sqlite3_cursor.executemany(
            """INSERT INTO "ExampleSqlSaver timestamp:1742837678014"(x,temperature) VALUES(:x,:temperature)""",
            [
                {"timestamp": time_stamp, "x": 0, "temperature": 0.6519844731250238},
                # {"timestamp": time_stamp, "x": 1, "temperature": 0.8307955603827071},
                # {"timestamp": time_stamp, "x": 2, "temperature": 0.9121215107754074},
                # {"timestamp": time_stamp, "x": 3, "temperature": 0.7356677089848823},
                # {"timestamp": time_stamp, "x": 4, "temperature": 0.6031502326540543},
                # {"timestamp": time_stamp, "x": 5, "temperature": 0.44179161623614216},
                # {"timestamp": time_stamp, "x": 6, "temperature": 0.5916372847789413},
                # {"timestamp": time_stamp, "x": 7, "temperature": 0.850536904323041},
                # {"timestamp": time_stamp, "x": 8, "temperature": 0.5886951158571079},
                # {"timestamp": time_stamp, "x": 9, "temperature": 0.024571036476593644},
            ],
        )

        await _sqlite3_connection.commit()

        await _sqlite3_connection.close()

    asyncio.run(main())

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
