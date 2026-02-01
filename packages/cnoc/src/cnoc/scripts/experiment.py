import asyncio
from contextlib import (
    redirect_stderr,
    redirect_stdout,
)
import datetime
import importlib
from io import StringIO

import os
import sys
from threading import Event, Lock
from traceback import print_tb
from urllib.parse import unquote
import json
from typing import Any, Callable, TypedDict, cast

from ..lib._params import params2Save
from ..lib.saver import Saver
from websockets import ConnectionClosed, Request, ServerConnection
from ..lib.exceptions import ExperimentEnded

from ..lib.manager import Manager

from .utils import preloadLocal

from ..lib.experiment import ExperimentABC

from ..lib.equipment import EquipmentABC
from websockets.asyncio.server import serve


def flush():
    print(end=None, flush=True)


class Runner:
    def __init__(
        self,
        experiment: ExperimentABC[Any],
        manager: Manager,
        equipments: dict[str, EquipmentABC[Any]],
        onLoopStart: Callable[[int], None],
        onPause: Callable[[], None],
        onEnd: Callable[[bool], None],
    ):
        self.experiment = experiment
        self.manager = manager
        self._experiment_lock = Lock()

        self.equipments = equipments

        self._onLoopStart = onLoopStart
        self._onPause = onPause
        self._onEnd = onEnd

        self._should_run = Event()

        self._should_stop_lock = Lock()
        self._should_stop = False

    @property
    def should_stop(self):
        with self._should_stop_lock:
            return self._should_stop

    @should_stop.setter
    def should_stop(self, value: bool):
        with self._should_stop_lock:
            self._should_stop = value

    def start(self):
        self._should_run.set()

    def pause(self):
        self._should_run.clear()

    def stop(self):
        self.should_stop = True
        self._should_run.set()

    def cont(self):
        self._should_run.set()

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
            with self._experiment_lock:
                res = eval(command, globals=globals(), locals=locals())
            print(f"{res}", flush=True)
            return

        except SyntaxError:
            pass
        except Exception as e:
            print(e, flush=True)
            return

        try:
            f = StringIO()

            with redirect_stdout(f):
                with redirect_stderr(sys.stdout):
                    with self._experiment_lock:
                        exec(command, globals=globals(), locals=locals())

            return

        except Exception as e:
            print(e, flush=True)

    def run(self):
        try:
            loop_count = -1
            while True:
                # Wait until the running event is set in each loop
                self._should_run.wait()

                # Stop the experiment is the stop event is set
                if self.should_stop:
                    self._onEnd(False)
                    return

                # Loop the experiment once with the newest index
                loop_count += 1
                try:
                    self._onLoopStart(loop_count)
                    with self._experiment_lock:
                        self.experiment.loop(
                            loop_count,
                            lambda: self.should_stop or not self._should_run.is_set(),
                        )
                    flush()

                except ExperimentEnded:
                    self._onEnd(True)
                    return

                # Pause the loop
                if not self._should_run.is_set():
                    # Decrement to exclude the previous loop index
                    loop_count -= 1
                    self._onPause()

        except Exception as e:
            print(f"{type(e).__name__} in experiment: {e}", flush=True)
            print_tb(sys.exc_info()[2])
            self._onEnd(False)
            return

    def close(self):
        self.stop()
        self.experiment.cleanup()


async def chart_handler(saver: Saver[Any], ws: ServerConnection):
    future: asyncio.Future[Any] = asyncio.Future()
    while True:
        try:
            saver._saver._subscribe(ws)  # pyright: ignore[reportPrivateUsage]
            await future
        except ConnectionClosed:
            pass
        except Exception as e:
            print(f"Error in chart websocket handler: {e}", flush=True)
            print(e, flush=True)
            print_tb(sys.exc_info()[2])
        finally:
            saver._saver._unsubscribe()  # pyright: ignore[reportPrivateUsage]
            future.cancel()


class ExperimentWsHandle:
    def __init__(self):
        pass

    async def handler(
        self,
        ws: ServerConnection,
        experiment: ExperimentABC[Any],
        manager: Manager,
        equipments: dict[str, EquipmentABC[Any]],
    ):
        self.ws = ws
        self.runner = Runner(
            experiment, manager, equipments, self.onLoopStart, self.onPause, self.onEnd
        )
        self.manager = manager
        self.manager._run_coroutine_threadsafe(asyncio.to_thread(self.runner.run))  # pyright: ignore[reportPrivateUsage]

        self.runner.start()
        try:
            async for message in ws:
                res = json.loads(message)
                match res["event"]:
                    case "pause":
                        self.runner.pause()
                    case "stop":
                        self.runner.stop()
                    case "continue":
                        self.runner.cont()
                    case "interpret":
                        if "name" in res["value"]:
                            self.runner.interpret(
                                res["value"]["command"], res["value"]["name"]
                            )

                        else:
                            self.runner.interpret(res["value"]["command"])

                    case _:
                        print(f"Invalid event {res['event']}", flush=True)
        except ConnectionClosed:
            pass
        except Exception as e:
            print(f"Error in experiment websocket handler: {e}", flush=True)
            print(e, flush=True)
            print_tb(sys.exc_info()[2])
        finally:
            self.runner.close()

    # START OF METHODS CALLED BY RUNNER

    def onLoopStart(self, loop_count: int):
        self.manager._run_coroutine_threadsafe(  # pyright: ignore[reportPrivateUsage]
            self.ws.send(json.dumps({"event": "loop_start", "loop_count": loop_count})),
        )

    def onPause(self):
        self.manager._run_coroutine_threadsafe(  # pyright: ignore[reportPrivateUsage]
            self.ws.send(json.dumps({"event": "paused"}))
        )

    def onEnd(self, loop_ended: bool):
        self.manager._run_coroutine_threadsafe(  # pyright: ignore[reportPrivateUsage]
            self.ws.send(json.dumps({"event": "ended", "loop_ended": loop_ended}))
        )
        self.manager._run_coroutine_threadsafe(self.ws.close())  # pyright: ignore[reportPrivateUsage]

    # END OF METHODS CALLED BY RUNNER


class AsyncApp:
    def __init__(
        self,
        manager: Manager,
        experiment: ExperimentABC[Any],
        equipments: dict[str, EquipmentABC[Any]],
    ):
        self.manager = manager
        self.experiment = experiment
        self.equipments = equipments

        self.task: asyncio.Task[Any] | None = None
        self.wss: list[ServerConnection] = []

    async def startServer(self):
        server = await serve(self.handler, "localhost", 8080)
        self.task = asyncio.create_task(server.serve_forever())

    async def handler(self, ws: ServerConnection):
        path = cast(Request, ws.request).path
        self.wss.append(ws)

        # Multiplex
        if path == "/experiment":
            ws_handle = ExperimentWsHandle()

            await ws_handle.handler(ws, self.experiment, self.manager, self.equipments)

            await ws.close()
            self.wss.remove(ws)

            await self.manager._close()  # pyright: ignore[reportPrivateUsage]

            for ws in self.wss:
                await ws.close()

            self.wss = []

            if self.task:
                self.task.cancel()

        elif path.startswith("/chart"):
            # unquote.split => ["", "chart", "<chart_title>"]
            await chart_handler(
                self.manager._savers[unquote(path).split("/")[2]],  # pyright: ignore[reportPrivateUsage]
                ws,
            )
            self.wss.remove(ws)


class App:
    def __init__(self):
        def parseSave(save: Save):
            name = save["name"]
            module = save["module"]
            cls = save["cls"]
            params = save["params"]
            instance = getattr(importlib.reload(importlib.import_module(module)), cls)()

            return name, instance, params

        self.equipments: dict[str, EquipmentABC[Any]] = {}

        # Load equipments
        if os.path.exists("./.beinn/equipments.json"):
            with open("./.beinn/equipments.json") as f:
                equipment_res: list[Save] = json.loads(f.read())
                equipment_params: dict[str, Any] = {}

                for save in equipment_res:
                    name, instance, params = parseSave(save)
                    self.equipments[name] = instance
                    equipment_params[name] = params

                for name, params in equipment_params.items():
                    self.equipments[name].setParams(
                        params, self.equipments, self.equipments[name].params.__class__
                    )

        # Load experiment
        with open("./.beinn/experiment.json") as f:
            experiment_res: Save = json.loads(f.read())
            name, instance, params = parseSave(experiment_res)

            self.experiment: ExperimentABC[Any] = instance

            self.experiment.setParams(
                params, self.equipments, self.experiment.params.__class__
            )

    async def start(self):
        self.timestamp = int(datetime.datetime.now().timestamp() * 1000)
        self.manager = Manager(
            self.timestamp,
            asyncio.get_running_loop(),
        )

        self.experiment.start(self.manager)

        async_app = AsyncApp(self.manager, self.experiment, self.equipments)

        await async_app.startServer()

        with open(f"./data/{self.timestamp}/snapshot.json", "w+") as f:
            snapshots = {}
            for name, equipment in self.equipments.items():
                snapshots[name] = equipment.snapshot()
            json.dump(snapshots, f)

        with open(f"./data/{self.timestamp}/params.json", "w+") as f:
            params = {}
            for name, equipment in self.equipments.items():
                params[name] = params2Save(equipment.params)
            params["experiment"] = params2Save(self.experiment.params)
            json.dump(params, f)

        # This asks beinn to connect to the websocket server
        print(
            json.dumps(
                {
                    "event": "started",
                    "timestamp": self.timestamp,
                    "expected_loop_count": self.manager.expected_loop_count,
                    "saver_configs": {
                        k: v._saver.config  # pyright: ignore[reportPrivateUsage]
                        for k, v in self.manager._savers.items()  # pyright: ignore[reportPrivateUsage]
                    },
                }
            ),
            flush=True,
        )

        try:
            if async_app.task:
                await async_app.task
        except asyncio.CancelledError:
            return
        except Exception as e:
            print(f"Error in App.start: {e}", flush=True)
            print(e, flush=True)
            print_tb(sys.exc_info()[2])
            return


class Save(TypedDict):
    name: str
    module: str
    cls: str
    params: dict[str, Any]


def main():
    app: App | None = None
    try:
        preloadLocal()
        app = App()

    except Exception as e:
        print(e, flush=True)
        print_tb(sys.exc_info()[2])
        sys.exit(1)

    # Start the websocket server and experiment
    asyncio.run(app.start())
