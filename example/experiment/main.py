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
        try:
            _sqlite3_connection = await aiosqlite.connect("data.db")
            _sqlite3_cursor = await _sqlite3_connection.cursor()
            time_stamp = math.floor(time.time() * 1000)

            print("hi")
            await _sqlite3_cursor.executescript("""
                                                CREATE TABLE "ExampleSqlSaver timestamp:8" (
                id INTEGER PRIMARY KEY,
                timestamp INTEGER,
    x REAL,
    temperature REAL
                ) """)
            await _sqlite3_cursor.executemany(
                """INSERT INTO "ExampleSqlSaver timestamp:8"(x,timestamp,temperature) VALUES(:x,:timestamp,:temperature)""",
                [
                    {
                        "x": 0,
                        "temperature": 0.8842598734536562,
                        "timestamp": 1742840284542,
                    },
                    {
                        "x": 1,
                        "temperature": 0.5620609419026966,
                        "timestamp": 1742840284542,
                    },
                    {
                        "x": 2,
                        "temperature": 0.9423298064982415,
                        "timestamp": 1742840284543,
                    },
                    {
                        "x": 3,
                        "temperature": 0.10515714630483097,
                        "timestamp": 1742840284543,
                    },
                    {
                        "x": 4,
                        "temperature": 0.4762397239741124,
                        "timestamp": 1742840284544,
                    },
                    {
                        "x": 5,
                        "temperature": 0.4582519633139812,
                        "timestamp": 1742840284544,
                    },
                    {
                        "x": 6,
                        "temperature": 0.7410067703889367,
                        "timestamp": 1742840284544,
                    },
                    {
                        "x": 7,
                        "temperature": 0.9470705377266845,
                        "timestamp": 1742840284545,
                    },
                    {
                        "x": 8,
                        "temperature": 0.3163335745289665,
                        "timestamp": 1742840284545,
                    },
                    {
                        "x": 9,
                        "temperature": 0.2608475478209309,
                        "timestamp": 1742840284545,
                    },
                ],
            )

            print("executed")

            await _sqlite3_connection.commit()

            print("commited")

            await _sqlite3_connection.close()

        except Exception as e:
            print(e)

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
