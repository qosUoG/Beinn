import asyncio
import importlib
import json
import sys
from threading import Lock
from threading import Event
from traceback import print_tb
from typing import Any, Coroutine, TypedDict

from websockets import ServerConnection

from packages.cnoc.src.cnoc.public.exceptions import ExperimentCompleted

from ..public.params import dict2Params

from ..public.equipment import EquipmentABC

from ..public.experiment import ExperimentABC
from ..public.manager import Manager


class State:
    def __init__(self):
        self._lock = Lock()
        self.should_run = Event()
        self._should_stop = False

    def start(self):
        self.should_run.set()
        self._should_stop = False

    def pause(self):
        self.should_run.clear()

    def stop(self):
        self.should_run.set()
        with self._lock:
            self._should_stop = True

    def cont(self):
        with self._lock:
            self._should_stop = False

    @property
    def should_stop(self):
        with self._lock:
            return self._should_stop


class Instance(TypedDict):
    name: str
    module: str
    cls: str
    params: dict[str, Any]


class Payload(TypedDict):
    equipments: list[Instance]
    experiment: Instance


class App:
    equipments: dict[str, EquipmentABC] = {}
    manager: Manager = Manager()

    experiment: ExperimentABC
    ws: ServerConnection
    loop: asyncio.EventLoop

    state: State = State()

    @classmethod
    def flush(cls):
        print(end=None, flush=True)

    @classmethod
    async def sendJson(cls, data: dict[str, Any]):
        await cls.ws.send(json.dumps(data))

    @classmethod
    def runCoroThreadsafe(cls, coro: Coroutine[Any, Any, None]):
        asyncio.run_coroutine_threadsafe(coro, cls.loop)

    @classmethod
    async def start(cls, res: dict[str, Any], ws: ServerConnection):
        cls.ws = ws
        cls.loop = asyncio.get_running_loop()
        # Load equipment and experiment
        payload: Payload = res["value"]
        equipments_payload = payload["equipments"]
        experiment_payload = payload["experiment"]

        # Load all equipment
        for e in equipments_payload:
            cls.equipments[e["name"]] = getattr(
                importlib.reload(importlib.import_module(e["module"])),
                e["cls"],
            )()

        # Load experiment
        cls.experiment = getattr(
            importlib.reload(importlib.import_module(experiment_payload["module"])),
            experiment_payload["cls"],
        )()

        # Set all equipment params
        for e in equipments_payload:
            cls.equipments[e["name"]].params = dict2Params(e["params"])

        # Set experiment params
        cls.experiment.params = dict2Params(experiment_payload["params"])

        # Run experiment start function
        await cls._initiate_experiment()

        # Run the experiment loops
        asyncio.create_task(asyncio.to_thread(cls._runner_wrapper))

    @classmethod
    async def _initiate_experiment(cls):
        await asyncio.to_thread(lambda: cls.experiment.start(cls.manager))
        # send started
        await cls.sendJson(
            {
                "event": "started",
                "expected_loop_count": cls.manager.expected_loop_count,
                "chart_configs": cls.manager.chartConfigs(),
                "saver_configs": cls.manager.saverConfigs(),
            }
        )

        cls.state.should_run.set()

    @classmethod
    def _runner_wrapper(cls):
        try:
            cls._runner()
            cls.flush()

        except Exception as e:
            print(f"{type(e).__name__} in experiment: {e}", flush=True)
            _, _, traceback = sys.exc_info()
            print_tb(traceback)
            cls.flush()

            cls._close()
            cls.flush()

            cls.runCoroThreadsafe(cls.sendJson({"event": "stopped"}))
            return

    def _runner(cls):
        loop_count = -1
        while True:
            # Wait until the running event is set in each loop
            cls.state.should_run.wait()

            # Stop the experiment is the stop event is set
            if cls.state.should_stop:
                # self._cnoc_experiment.cleanup()
                cls.state.should_run.clear()

                cls._close()
                cls.flush()

                cls.runCoroThreadsafe(cls.sendJson({"event": "stopped"}))
                return

            # Loop the experiment once with the newest index
            loop_count += 1
            cont = cls._loop(loop_count)

            if not cont:
                return

            # Pause the loop
            if not cls.state.should_run.is_set():
                # Decrement to exclude the previous loop index
                loop_count -= 1

                cls.runCoroThreadsafe(cls.sendJson({"event": "paused"}))

    @classmethod
    def _loop(cls, index: int):
        try:
            cls.runCoroThreadsafe(
                cls.sendJson({"event": "loop_start", "loop_count": index})
            )
            cls.experiment.loop(index)

            cls.flush()

            return True

        except ExperimentCompleted:
            cls._close()

            cls.runCoroThreadsafe(cls.sendJson({"event": "completed"}))

            return False

    @classmethod
    def _close(cls):
        cls.experiment.cleanup()
        cls.manager.close()
        for e in cls.equipments.values():
            e.cleanup()
