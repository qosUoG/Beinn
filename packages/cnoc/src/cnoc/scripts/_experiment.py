import asyncio
from contextlib import redirect_stderr, redirect_stdout
import importlib
from io import StringIO
import json
import sys
from threading import Lock, Thread
from threading import Event
from traceback import print_tb
from typing import Any, Coroutine, TypedDict

from websockets import ServerConnection

from ..public.exceptions import ExperimentEnded

from ..public.equipment import EquipmentABC

from ..public.experiment import ExperimentABC
from ..public.manager import Manager


def flush():
    print(end=None, flush=True)


class _State:
    def __init__(self):
        self._lock = Lock()
        self.should_run = Event()
        self._should_stop = False
        self._ended: bool = False
        self._force_stop: bool = False

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

    @property
    def ended(self):
        with self._lock:
            return self._ended

    @ended.setter
    def ended(self, value: bool):
        with self._lock:
            self._ended = value

    @property
    def force_stop(self):
        with self._lock:
            return self._force_stop

    def kill(self):
        with self._lock:
            self._force_stop = True
        self.stop()


class Instance(TypedDict):
    name: str
    module: str
    cls: str
    params: dict[str, Any]


class Payload(TypedDict):
    equipments: list[Instance]
    experiment: Instance


class App:
    # A thread safe wrapper of App
    def __init__(
        self, ws: ServerConnection, loop: asyncio.AbstractEventLoop, res: Payload
    ):
        self._lock: Lock = Lock()
        self._loop = loop
        self._ws = ws
        self.manager = Manager()
        self._state = _State()

        self._equipments: dict[str, EquipmentABC] = {}
        self._experiment: ExperimentABC

        equipments_payload = res["equipments"]
        experiment_payload = res["experiment"]

        # Load all equipment
        for e in equipments_payload:
            self._equipments[e["name"]] = getattr(
                importlib.reload(importlib.import_module(e["module"])),
                e["cls"],
            )()

        # Load experiment
        self._experiment = getattr(
            importlib.reload(importlib.import_module(experiment_payload["module"])),
            experiment_payload["cls"],
        )()

        # Set all equipment params
        for e in equipments_payload:
            self._equipments[e["name"]].setParams(
                e["params"],
                self._equipments,
                self._equipments[e["name"]].params.__class__,
            )

        # Set experiment params
        self._experiment.setParams(
            experiment_payload["params"],
            self._equipments,
            self._experiment.params.__class__,
        )

    def _runCoroThreadsafe(self, coro: Coroutine[Any, Any, None]):
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    def _sendJson(self, data: dict[str, Any]):
        self._runCoroThreadsafe(self._ws.send(json.dumps(data)))

    def _ended_event(self, loop_ended: bool):
        flush()
        self._state.ended = True
        self._sendJson({"event": "ended", "loop_ended": loop_ended})

    def _paused_event(self):
        self._sendJson({"event": "paused"})

    def _loop_start_event(self, index: int):
        self._sendJson({"event": "loop_start", "loop_count": index})

    async def start(self):
        # Run experiment start function
        await asyncio.to_thread(self.initiate)

        # Run the experiment loops
        Thread(target=self._runner).start()

    def pause(self):
        self._state.pause()

    def stop(self):
        self._state.stop()

    def cont(self):
        self._state.cont()

    def kill(self):
        self._state.kill()
        self.close()

    @property
    def ended(self):
        return self._state.ended

    def initiate(self):
        with self._lock:
            try:
                self._experiment.start(self.manager)
            except Exception as e:
                if self._state.force_stop:
                    return
                print(f"Error starting experiment: {e}", flush=True)
                print_tb(sys.exc_info()[2])
                self._ended_event(False)
                return
            # send started

            self._sendJson(
                {
                    "event": "started",
                    "expected_loop_count": self.manager.expected_loop_count,
                    "chart_configs": {
                        k: v.getConfig() for k, v in self.manager.charts.items()
                    },
                    "saver_configs": [s.saver.path for s in self.manager.savers],
                }
            )

            self._state.should_run.set()

    def saveNote(self, note: str):
        with self._lock:
            if self.manager.savers:
                for saver in self.manager.savers:
                    saver.saver.saveNote(note)

    def interpret(self, command: str, name: str | None = None):
        try:
            if name is not None:
                command = command.replace(name, f"self.equipments['{name}']")

        except KeyError:
            print(f"{name} is not found in the list of equipments", flush=True)
            return
        except Exception as e:
            print(e, flush=True)
            return

        try:
            with self._lock:
                print(
                    f"{eval(command, globals=globals())}",
                    flush=True,
                )
            return

        except SyntaxError:
            pass
        except Exception as e:
            print(e, flush=True)
            return

        try:
            with self._lock:
                f = StringIO()

                with redirect_stdout(f):
                    with redirect_stderr(sys.stdout):
                        exec(command, globals=globals())

            return

        except Exception as e:
            print(e, flush=True)
            return

    def _runner(self):
        try:
            loop_count = -1
            while True:
                # Wait until the running event is set in each loop
                self._state.should_run.wait()

                # Stop the experiment is the stop event is set
                if self._state.should_stop:
                    self._ended_event(False)
                    return

                # Loop the experiment once with the newest index
                loop_count += 1
                try:
                    self._loop_start_event(loop_count)
                    with self._lock:
                        self._experiment.loop(
                            loop_count,
                            self._state.shouldStop,
                        )
                    flush()

                except ExperimentEnded:
                    self._ended_event(True)
                    return

                # Pause the loop
                if not self._state.should_run.is_set():
                    # Decrement to exclude the previous loop index
                    loop_count -= 1
                    self._paused_event()

        except Exception as e:
            if self._state.force_stop:
                return
            print(f"{type(e).__name__} in experiment: {e}", flush=True)
            print_tb(sys.exc_info()[2])
            self._ended_event(False)
            return

    def close(self):
        self._lock.acquire(True, 1)
        self._experiment.cleanup()
        for chart in self.manager.charts.values():
            chart.stop()
        for saver in self.manager.savers:
            saver.saver.close()
        for e in self._equipments.values():
            e.cleanup()
        self._lock.release()
