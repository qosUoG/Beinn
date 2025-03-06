from asyncio import Task
import asyncio
from threading import Condition, Event, Thread
from typing import TypedDict
from qoslablib import labtype as l, params as p, exceptions as e


class ExperimentThread(TypedDict):
    t: Thread
    end_event: Event


class AppState:
    project = {"path": ""}
    equipments: dict[str, l.Equipment] = {}
    experiments: dict[str, l.Experiment] = {}
    experiment_tasks: dict[str, Task] = {}
    experiment_stop_events: dict[str, Event] = {}
    experiment_pause_events: dict[str, Event] = {}

    @classmethod
    def start_experiment(cls, name: str):
        cls.experiment_stop_events[name] = Event()
        cls.experiment_pause_events[name] = Event()
        cls.experiment_tasks[name] = asyncio.create_task(
            asyncio.to_thread(
                _experiment_runner,
                cls.experiments[name],
                cls.experiment_stop_events[name],
                cls.experiment_pause_events[name],
            )
        )

    @classmethod
    def pause_experiment(cls, name: str):
        cls.experiment_pause_events[name].set()

    @classmethod
    def continue_experiment(cls, name: str):
        cls.experiment_pause_events[name].clear()

    @classmethod
    def stop_experiment(cls, name: str):
        cls.experiment_stop_events[name].set()


def _experiment_runner[T](_inst: type[T], stop_event: Event, pause_event: Event):
    index = 0
    while True:
        if stop_event.is_set():
            print("experiment stopped")
            return

        if not pause_event.is_set():
            try:
                _inst.loop(index)
                index += 1

            except e.ExperimentEnded:
                print("experiment ended")
                return
