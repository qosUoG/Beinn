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

from lib.ExampleExperiment import ExampleExperiment


if __name__ == "__main__":
    a = ExampleExperiment()
    print(inspect.getsource(inspect.getmodule(a)))
