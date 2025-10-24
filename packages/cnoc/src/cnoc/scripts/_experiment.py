import asyncio
import importlib
import json
import sys
from threading import Lock, Thread
from threading import Event
from traceback import print_tb
from typing import Any, Coroutine, TypedDict

from websockets import ServerConnection

from ..public.exceptions import ExperimentEnded

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
        with self._lock:
            self._should_stop = True
        self.should_run.set()

    def cont(self):
        with self._lock:
            self._should_stop = False
        self.should_run.set()

    def shouldStop(self):
        with self._lock:
            if self.should_run.is_set() and self._should_stop:
                return True

        if not self.should_run.is_set():
            return True

        return False

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
    task: asyncio.Task

    equipments: dict[str, EquipmentABC] = {}
    manager: Manager = Manager()

    experiment: ExperimentABC
    ws: ServerConnection
    loop: asyncio.EventLoop

    state: State = State()

    @classmethod
    def _flush(cls):
        print(end=None, _flush=True)

    @classmethod
    async def sendJson(cls, data: dict[str, Any]):
        await cls.ws.send(json.dumps(data))

    @classmethod
    def runCoroThreadsafe(cls, coro: Coroutine[Any, Any, None]):
        asyncio.run_coroutine_threadsafe(coro, cls.loop)

    @classmethod
    async def start(cls, res: Payload, ws: ServerConnection):
        cls.ws = ws
        cls.loop = asyncio.get_running_loop()
        # Load equipment and experiment

        equipments_payload = res["equipments"]
        experiment_payload = res["experiment"]

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
            cls.equipments[e["name"]].params = dict2Params(e["params"], cls.equipments)

        # Set experiment params
        cls.experiment.params = dict2Params(
            experiment_payload["params"], cls.equipments
        )

        # Run experiment start function
        await cls._initiate_experiment()

        # Run the experiment loops
        Thread(target=cls._runner_wrapper).start()

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
        cls._runner()
        cls.ws.close()
        cls.task.cancel()

    # All following methods are called from the runner thread
    @classmethod
    def _runner(cls):
        try:
            loop_count = -1
            while True:
                # Wait until the running event is set in each loop
                cls.state.should_run.wait()

                # Stop the experiment is the stop event is set
                if cls.state.should_stop:
                    cls._ended_event()
                    return

                # Loop the experiment once with the newest index
                loop_count += 1
                try:
                    cls._loop_start_event(loop_count)
                    cls.experiment.loop(
                        loop_count,
                        cls.state.shouldStop,
                    )
                    cls._flush()

                except ExperimentEnded:
                    cls._ended_event()
                    return

                # Pause the loop
                if not cls.state.should_run.is_set():
                    # Decrement to exclude the previous loop index
                    loop_count -= 1
                    cls._paused_event()

        except Exception as e:
            print(f"{type(e).__name__} in experiment: {e}", flush=True)
            print_tb(sys.exc_info()[2])
            cls._flush()
            cls._ended_event()
            return

    @classmethod
    def _ended_event(cls):
        cls._close()
        cls._flush()
        cls.runCoroThreadsafe(cls.sendJson({"event": "ended"}))

    @classmethod
    def _paused_event(cls):
        cls.runCoroThreadsafe(cls.sendJson({"event": "paused"}))

    @classmethod
    def _loop_start_event(cls, index: int):
        cls.runCoroThreadsafe(
            cls.sendJson({"event": "loop_start", "loop_count": index})
        )

    @classmethod
    def _close(cls):
        cls.experiment.cleanup()
        cls.manager.close()
        for e in cls.equipments.values():
            e.cleanup()
