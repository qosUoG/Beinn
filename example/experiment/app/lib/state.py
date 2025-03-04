from threading import Event, Thread
from typing import TypedDict
from qoslablib import labtype as l, params as p, exceptions as e


class ExperimentThread(TypedDict):
    t: Thread
    end_event: Event


class AppState:
    project = {"path": ""}
    equipments: dict[str, l.Equipment] = {}
    experiments_threads: dict[str, ExperimentThread] = {}

    @classmethod
    def reset_dicts(cls):
        for et in cls.experiments_threads.values():
            et["end_event"].set()
            et["t"].join()
        cls.experiments_threads.clear()
        cls.equipments.clear()

    @classmethod
    def register_experiment[T](
        cls, name: str, params: dict[str, p.AllParamTypes], eCls: type[T]
    ):
        cls.experiments_threads[name] = {"end_event": Event()}
        cls.experiments_threads[name]["t"] = Thread(
            target=cls.experiment_runner,
            args=(cls.experiments_threads[name]["end_event"], params, eCls),
        )

    @classmethod
    def start_experiments(cls):
        for et in cls.experiments_threads.values():
            et["t"].start()

    def experiment_runner[T](
        event: Event, params: dict[str, p.AllParamTypes], eCls: type[T]
    ):
        _inst = eCls(params)
        index = 0
        while True:
            try:
                _inst.loop(index)
                index += 1
                if event.is_set():
                    print("experiment stopped")
                    return
            except e.ExperimentEnded:
                print("experiment ended")
                return
