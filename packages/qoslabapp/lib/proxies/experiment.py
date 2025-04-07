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
from qoslablib.params import ExperimentParamsToBackup, Params
from qoslablib.runtime import ExperimentABC

from qoslablib.runtime import ManagerABC

from .chart import ChartProxy
from .sql_saver import SqlSaverProxy

from ..settings.foundation import ExperimentStatus, Foundation


from ..utils.messenger import Messenger


class ExperimentRunner:
    class PreviousNotFinished(Exception):
        pass

    def __init__(
        self,
        experiment: ExperimentABC,
        messenger: Messenger,
    ):
        self._experiment = experiment
        self._messenger = messenger

        self._running = Event()
        self._should_run = Event()
        self._should_stop = Event()
        self._ran = Event()
        self._pid: int

    def prepare(self, status: ExperimentStatus):
        # The previous run, if there is one, shall not be running
        if hasattr(self, "_runner_task") and not self._runner_task.done():
            raise ExperimentRunner.PreviousNotFinished

        # Make sure the experiment starts in a fresh state
        self._iteration_count = -1

        self._running.clear()
        self._should_run.clear()
        self._should_stop.clear()
        status.stopped.clear()
        status.success.clear()
        self._ran.clear()

    def start(self, status: ExperimentStatus):
        self._runner_task = asyncio.create_task(self._start(status))

        self._should_run.set()

    async def _start(self, status: ExperimentStatus):
        res = await asyncio.to_thread(self._runner)
        if res:
            status.success.set()
        else:
            status.success.clear()

        status.stopped.set()

    def stop(self):
        self._should_stop.set()
        # Set the running event as well just in case it is being paused
        self._should_run.set()

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
                    return False

                # Loop the _experiment once with the newest index

                with self._iterate():
                    self._iteration_count += 1

                    try:
                        self._experiment.loop(self._iteration_count)
                        print("", end="", flush=True)

                    except ExperimentEnded:
                        print("experiment ended", flush=True)
                        return True

                    if not self._should_run.is_set():
                        # Decrement to exclude the previous loop index
                        self._iteration_count -= 1
        except Exception as e:
            print("Exception in experiment runner", flush=True)
            print(e, flush=True)
            return False


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

        # Status
        self._status: ExperimentStatus

        # Runner
        self._runner = ExperimentRunner(
            self._experiment,
            self._messenger,
        )

        self._params_backup: dict[str, dict[str, str]]

    """Public Interface of self"""

    async def forceStop(self):
        # Stop the runner
        self._runner.forceStop()

        # Cancel _done_task
        if hasattr(self, "_done_task"):
            self._done_task.cancel()

        # Chart gracefully shutdown itself
        for chart in self._charts.values():
            await chart.forceStop()

        # Still try to gracefully clean up sql_savers as there may be important data
        for sql_saver in self._sql_savers.values():
            await sql_saver.cleanup()

        # Shutting down the queue shall close the websocket if there is one
        self._messenger.shutdown()

    def removable(self):
        # Can only remove experiment that is not currently running
        return self._runner.removable()

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
        self._status = ExperimentStatus(
            ExperimentParamsToBackup(self.experiment_id, self._experiment.params)
        )
        # Prepare the runner
        try:
            self._runner.prepare(self._status)
        except ExperimentRunner.PreviousNotFinished:
            raise Exception("Previous Not finished")

        # Manager functions are also executed in the initalize function

        self._experiment.initialize(self)

        # Schedule the done procedure before starting the runner
        self._done_task = asyncio.create_task(self._doneExperiment())

        self._runner.start(self._status)

    async def _doneExperiment(self):
        await self._status.stopped.wait()

        # Charts shutdown itself

        # Clean up sql_savers
        for sql_saver in self._sql_savers.values():
            await sql_saver.cleanup()

        if self._status.success:
            self._messenger.put("status", "completed")
        else:
            self._messenger.put("status", "stopped")

    def _saveParams(self):
        pass

    def stop_async(self):
        self._runner.stop()

    async def waitUntil_stopped(self):
        if hasattr(self, "_status"):
            await self._status.stopped.wait()

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
            status=self._status,
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
            status=self._status,
            sql_saverT=sql_saverT,
            kwargs=kwargs,
        )

        return self._sql_savers[title]._sql_saver
