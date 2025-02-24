from threading import Thread
from qoslabpy import labtype as l


class AppState:
    project = {"path": ""}
    equipments: dict[str, l.Equipment] = {}
    experiments_threads: dict[str, Thread] = {}
