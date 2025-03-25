import asyncio

from contextlib import contextmanager

import os
import signal
from threading import Event
from typing import Any, override


from fastapi import WebSocket

from qoslablib.exceptions import ExperimentEnded
from qoslablib.extensions.chart import ChartABC

from qoslablib.extensions.saver import SqlSaverABC
from qoslablib.params import Params
from qoslablib.runtime import ExperimentABC

from qoslablib.runtime import ManagerABC

from .chart import ChartProxy
from .sql_saver import SqlSaverProxy

from ..settings.foundation import Foundation


from ..utils.messenger import Messenger


class ExperimentRunner:
    class PreviousNotFinished(Exception):
        pass

    def __init__(self, experiment: ExperimentABC, messenger: Messenger):
        self._experiment = experiment
        self._messenger = messenger

        self._running = Event()
        self._should_run = Event()
        self._should_stop = Event()
        self._stopped = Event()
        self._ran = Event()

        self._pid: int

    def prepare(self):
        # The previous run, if there is one, shall not be running
        if hasattr(self, "_runner_task") and not self._runner_task.done():
            raise ExperimentRunner.PreviousNotFinished

        # Make sure the experiment starts in a fresh state
        self._iteration_count = -1

        self._running.clear()
        self._should_run.clear()
        self._should_stop.clear()
        self._stopped.clear()
        self._ran.clear()

    def start(self):
        self._runner_thread = asyncio.to_thread(self._runner)
        self._runner_task = asyncio.create_task(self._runner_thread)

        self._should_run.set()

    def stop(self):
        self._should_stop.set()
        # Set the running event as well just in case it is being paused
        self._should_run.set()

    def waitUntil_stopped(self):
        self._stopped.wait()

    def pause(self):
        self._should_run.clear()

    def waitUntil_paused(self):
        self._ran.wait()

    def unpause(self):
        self._should_run.set()

    def forceStop(self):
        if hasattr(self, "_runner_task"):
            # Unconditionally killing the thread
            os.kill(self._pid, signal.SIGTERM)
            # Cancel the task
            self._runner_task.cancel()

    def removable(self):
        # Only removable if the experiment is done, i.e. stopped or completed or raised exception
        if hasattr(self, "_runner_task"):
            return self._runner_task.done()

        return True

    """All methods below are consumed in the runner thread"""

    @contextmanager
    def _iterate(self):
        try:
            self._running.set()
            self._ran.clear()
            yield
        finally:
            self._running.clear()
            self._ran.set()
            # Post loop count event to message queue
            self._messenger.put_threadsafe("iteration_count", self._iteration_count)

    def _runner(self):
        try:
            self._pid = os.getpid()

            # Post Start event to message queue
            self._messenger.put_threadsafe("status", "started")

            while True:
                # Wait until the running event is set in each loop
                self._should_run.wait()

                # Stop the _experiment is the stop event is set
                if self._should_stop.is_set():
                    self._experiment.stop()
                    self._should_run.clear()
                    self._stopped.set()
                    return

                # Loop the _experiment once with the newest index

                with self._iterate():
                    self._iteration_count += 1

                    try:
                        self._experiment.loop(self._iteration_count)

                    except ExperimentEnded:
                        print("experiment ended")
                        self._stopped.set()
                        self._messenger.put_threadsafe("status", "completed")
                        return

                    if not self._should_run.is_set():
                        # Decrement to exclude the previous loop index
                        self._iteration_count -= 1
        except Exception as e:
            print("Exception in experiment runner")
            print(e)


class ExperimentProxy(ManagerABC):
    class NotRemovable(Exception):
        pass

    def __init__(
        self,
        *,
        id: str,
        experimentCls: type[ExperimentABC],
    ):
        # Experiment Instance
        self.experiment_id = id
        self._experiment = experimentCls()

        # Extensions
        self._charts: dict[str, ChartProxy] = {}
        self._sql_savers: dict[str, SqlSaverProxy] = {}

        # Messenger
        self._messenger = Messenger(Foundation.getLoop())
        self._subscriber: WebSocket

        # Runner
        self._runner = ExperimentRunner(self._experiment, self._messenger)

    """Public Interface of self"""

    async def cleanup(self):
        if not self._runner.removable():
            raise ExperimentProxy.NotRemovable

        # Shutting down the queue shall close the websocket if there is one
        self._messenger.shutdown()

        # Clean up charts
        for chart in self._charts.values():
            await chart.cleanup()

        # Clean up sql_savers
        for sql_saver in self._sql_savers.values():
            await sql_saver.cleanup()

    """Public Interface to messenger"""

    def subscribeMessage(self, ws: WebSocket):
        self._subscriber = ws

        def unsubscribe():
            del self._subscriber

        return (self._getMessage, unsubscribe)

    async def _getMessage(self):
        return await self._messenger.get()

    """Public Interface to experiment"""

    @property
    def params(self):
        return self._experiment.params

    @params.setter
    def params(self, params: Params):
        self._experiment.params = params

    """Public Interface to runner"""

    def start(self):
        # Prepare the runner
        try:
            self._runner.prepare()
        except ExperimentRunner.PreviousNotFinished:
            self._messenger.put("error", "PreviousNotFinished")

        # Initialize and send the proposed total iteration
        self._experiment.initialize(self)

        self._runner.start()

    def stop_async(self):
        self._runner.stop()

    def waitUntil_stopped(self):
        self._runner.waitUntil_stopped()

    def stop_sync(self):
        self.stop_async()
        self._runner.waitUntil_stopped()
        self._messenger.put("status", "stopped")

    def forceStop(self):
        self._runner.forceStop()
        self._messenger.put("status", "stopped")

    def pause_async(self):
        self._runner.pause()

    def pause_sync(self):
        self.pause_async()
        self._runner.waitUntil_paused()
        self._messenger.put("status", "paused")

    def unpause(self):
        self._runner.unpause()
        self._messenger.put("status", "continued")

    """Experiment Manager override"""

    @override
    def suggestTotalIterations(self, total_iterations: int):
        self._messenger.put("proposed_total_iterations", total_iterations)

    """Chart Manager override"""

    @override
    def createChart(self, chartT: ChartABC, kwargs: Any = {}):
        title = kwargs["title"]

        self._charts[title] = ChartProxy(
            chartT=chartT,
            kwargs=kwargs,
        )

        self._messenger.put("chart_config", self._charts[title].getConfig())
        return self._charts[title]._chart

    """Public Interface to Chart"""

    def subscribeChart(self, title: str, ws: WebSocket):
        return self._charts[title].subscribe(ws)

    """Sql Saver Manager override"""

    @override
    def createSqlSaver(self, sql_saverT: type[SqlSaverABC], kwargs: Any = {}):
        title = kwargs["title"]

        self._sql_savers[title] = SqlSaverProxy(
            sql_saverT=sql_saverT,
            kwargs=kwargs,
        )

        return self._sql_savers[title]._sql_saver
