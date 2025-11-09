import asyncio
from contextlib import (
    redirect_stderr,
    redirect_stdout,
)
import importlib
from io import StringIO

import os
import sys
from threading import Event, Lock
from traceback import print_tb
from urllib.parse import unquote
import json
from typing import Any, Callable, TypedDict, cast
from websockets import ConnectionClosed, Request, ServerConnection


from ..public.charts._chart import ChartABC
from ..public.exceptions import ExperimentEnded

from ..public.manager import Manager

from .utils import preloadLocal

from ..public.experiment import ExperimentABC

from ..public.equipment import EquipmentABC
from websockets.asyncio.server import serve

# # from ._experiment import App
# from .utils import preloadLocal


# class StartPayload(TypedDict):
#     equipments: list[InstancePayload]
#     experiment: InstancePayload


# async def chartHandler(chart_name: str, ws: ServerConnection):
#     # Subscribe websocket to chart stream
#     # chart = Globals.app.manager.charts[chart_name]

#     try:
#         # async for frames in chart.subscribe():
#         #     if frames:
#         #         await ws.send(frames)

#         await ws.close(4000)
#     except ConnectionClosed:
#         # Globals.wss.remove(ws)
#         pass
#     # await ws.wait_closed()


# async def experimentHandler(ws: ServerConnection):


def flush():
    print(end=None, flush=True)


class Runner:
    def __init__(
        self,
        experiment: ExperimentABC[Any],
        manager: Manager,
        onLoopStart: Callable[[int], None],
        onPause: Callable[[], None],
        onEnd: Callable[[bool], None],
    ):
        self.experiment = experiment
        self.manager = manager
        self._experiment_lock = Lock()

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

    def saveNote(self, note: str):
        with self._experiment_lock:
            if self.manager.savers:
                for saver in self.manager.savers:
                    saver.saver.saveNote(note)

    def interpret(self, command: str, name: str | None = None):
        with self._experiment_lock:
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
                f = StringIO()

                with redirect_stdout(f):
                    with redirect_stderr(sys.stdout):
                        exec(command, globals=globals())

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


class ChartWsHandle:
    def __init__(
        self,
        chart: ChartABC,
        ws: ServerConnection,
    ):
        self.chart = chart
        self.ws = ws

    def send(self, data: bytes):
        asyncio.run_coroutine_threadsafe(self.ws.send(data), self.ws.loop)

    async def handler(self):
        while True:
            try:
                self.chart.subscribe(self.send)
            except ConnectionClosed:
                self.chart.unsubscribe()
            except Exception as e:
                self.chart.unsubscribe()
                print(f"Error in chart websocket handler: {e}", flush=True)
                print(e, flush=True)
                print_tb(sys.exc_info()[2])
                return


class ExperimentWsHandle:
    def __init__(self):
        pass

    async def handler(
        self, ws: ServerConnection, experiment: ExperimentABC[Any], manager: Manager
    ):
        self.ws = ws
        runner = Runner(experiment, manager, self.onLoopStart, self.onPause, self.onEnd)
        asyncio.create_task(asyncio.to_thread(runner.run))
        runner.start()
        try:
            async for message in ws:
                res = json.loads(message)
                match res["event"]:
                    case "pause":
                        runner.pause()
                    case "stop":
                        runner.stop()
                    case "continue":
                        runner.cont()
                    case "save_note":
                        runner.saveNote(res["value"])
                    case "interpret":
                        if "name" in res["value"]:
                            runner.interpret(
                                res["value"]["command"], res["value"]["name"]
                            )

                        else:
                            runner.interpret(res["value"]["command"])

                    case _:
                        print(f"Invalid event {res['event']}", flush=True)
        except ConnectionClosed:
            return
        except Exception as e:
            print(f"Error in experiment websocket handler: {e}", flush=True)
            print(e, flush=True)
            print_tb(sys.exc_info()[2])
            return

        # START OF METHODS CALLED BY RUNNER

    def onLoopStart(self, loop_count: int):
        asyncio.run_coroutine_threadsafe(
            self.ws.send(json.dumps({"event": "loop_start", "loop_count": loop_count})),
            self.ws.loop,
        )

    def onPause(self):
        asyncio.run_coroutine_threadsafe(
            self.ws.send(json.dumps({"event": "paused"})), self.ws.loop
        )

    def onEnd(self, loop_ended: bool):
        asyncio.run_coroutine_threadsafe(
            self.ws.send(json.dumps({"event": "ended", "loop_ended": loop_ended})),
            self.ws.loop,
        )

    # END OF METHODS CALLED BY RUNNER


class AsyncApp:
    def __init__(self, manager: Manager, experiment: ExperimentABC[Any]):
        self.task: asyncio.Task[Any] | None = None
        self.manager = manager
        self.experiment = experiment
        self.wss: list[ServerConnection] = []

    async def startServer(self):
        server = await serve(self.handler, "localhost", 8080)
        self.task = asyncio.create_task(server.serve_forever())

    async def handler(self, ws: ServerConnection):
        path = cast(Request, ws.request).path
        self.wss.append(ws)

        # Multiplex
        if path == "/experiment":
            await ExperimentWsHandle().handler(ws, self.experiment, self.manager)
            self.wss.remove(ws)

        elif path.startswith("/chart"):
            # unquote.split => ["", "chart", "<chart_title>"]
            await ChartWsHandle(
                self.manager.charts[unquote(path).split("/")[2]], ws
            ).handler()
            self.wss.remove(ws)

        elif path == "/close":
            await asyncio.gather(*[ws.close() for ws in self.wss])
            if self.task:
                self.task.cancel()


class App:
    def __init__(self):
        self.manager = Manager()
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

            self.experiment = instance

    def initiate(self):
        self.experiment.start(self.manager)

    async def start(self):
        async_app = AsyncApp(self.manager, self.experiment)

        await async_app.startServer()

        # This asks beinn to connect to the websocket server
        print(
            {
                json.dumps(
                    {
                        "event": "started",
                        "expected_loop_count": self.manager.expected_loop_count,
                        "chart_configs": {
                            k: v.getConfig() for k, v in self.manager.charts.items()
                        },
                        "saver_configs": [s.saver.path for s in self.manager.savers],
                    }
                )
            },
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


def parseSave(save: Save):
    name = save["name"]
    module = save["module"]
    cls = save["cls"]
    params = save["params"]
    instance = getattr(importlib.reload(importlib.import_module(module)), cls)()

    return name, instance, params


def main():
    try:
        preloadLocal()
        app = App()

        # Initiate the experiment
        app.initiate()

    except Exception as e:
        print(json.dumps({"event": "error"}), flush=True)
        print(e, flush=True)
        print_tb(sys.exc_info()[2])
        sys.exit(1)

    # Start the websocket server and experiment
    asyncio.run(app.start())
