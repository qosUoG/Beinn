import asyncio
import os
import pickle
from threading import Event
import time
from types import CoroutineType
from typing import Any, TypedDict, override


from fastapi import WebSocket

from cnoc.exceptions import ExperimentEnded
from cnoc.extensions.chart import _ChartABC

from cnoc.extensions.saver import _SaverABC

from ..utils.params import Params, experimentParams2Backup
from cnoc.experiment import ExperimentABC

from cnoc.managers import ManagerABC

from .chart import ChartProxy
from .saver import SaverProxy

from ..settings.foundation import Foundation


from ..utils.messenger import Messenger


class _Manager(ManagerABC):
    def __init__(self, *, suggestTotalIterations, createChart, createSaver):
        self._suggestTotalIterations = suggestTotalIterations
        self._createChart = createChart
        self._createSaver = createSaver

    @override
    def suggestTotalIterations(self, total_iterations):
        self._suggestTotalIterations(total_iterations)

    @override
    def createChart(self, chartT, kwargs):
        return self._createChart(chartT, kwargs)

    @override
    def createSaver(self, saverT, kwargs):
        return self._createSaver(saverT, kwargs)


class ExperimentProxy:
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
        self._savers: dict[str, SaverProxy] = {}

        # Manager
        self._manager = _Manager(
            suggestTotalIterations=self.suggestTotalIterations,
            createChart=self.createChart,
            createSaver=self.createSaver,
        )

        # Messenger
        self._messenger = Messenger(Foundation.getLoop())
        self._subscriber: WebSocket

        # runner status
        self._running = Event()
        self._not_running = Event()
        self._should_run = Event()
        self._should_stop = Event()

    def _runner(self):
        """
        lifecycle of the function:

        MESSAGE   started

        --- LOOP ---
        WAIT        should_run
        IF          should_stop
        | RUN       experiment.stop()
        | CLEAR     should_run              --> RETURN False

        SET         running
        CLEAR       not_running
        ()          experiment.loop()
        | EXCEPT    ExperimentEnded         --> RETURN True

        IF          !should_run
        | RUN       iteration_count -= 1

        CLEAR       running
        SET         not_running
        MESSAGE     iteration_count


        """
        try:
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

                self._running.set()
                self._not_running.clear()
                self._iteration_count += 1

                try:
                    self._experiment.loop(self._iteration_count)
                    # flush stdout
                    print("", end="", flush=True)

                except ExperimentEnded:
                    print("experiment ended", flush=True)
                    return True

                if not self._should_run.is_set():
                    # Decrement to exclude the previous loop index
                    self._iteration_count -= 1

                self._running.clear()
                self._not_running.set()
                # Post loop count event to message queue
                self._messenger.put_threadsafe("iteration_count", self._iteration_count)
        except Exception as e:
            print("Exception in experiment runner", flush=True)
            print(e, flush=True)
            return False

    def start(self):
        if hasattr(self, "_runner_task") and not self._runner_task.done():
            # frontend did not realize experiment is still running
            raise Exception("Previous Not finished")

        # Make sure the experiment starts in a fresh state
        self._iteration_count = -1
        self._running.clear()
        self._should_run.clear()
        self._should_stop.clear()
        self._not_running.clear()

        self._timestamp = int(time.time() * 1000)

        self._experiment.initialize(self._manager)

        # Event for signaling finishing cancel
        self._cancelled = asyncio.Event()
        self._runner_task = asyncio.create_task(self.runner_thread_holder())

        self._should_run.set()

    async def runner_thread_holder(self):
        try:
            success = await asyncio.to_thread(self._runner)

            for saver in self._savers.values():
                data = await saver.finalize()

                meta = experimentParams2Backup(
                    self.experiment_id, self._experiment.params
                )

                filename = f"./data/{saver.title}.pickle"

                if not os.path.isfile(filename):
                    with open(filename, "wb") as f:
                        pickle.dump({self._timestamp: {"data": data, "meta": meta}}, f)

                else:
                    # Read the past data
                    class Entry(TypedDict):
                        data: Any
                        meta: dict[str, dict[str, str]]

                    with open(filename, "rb") as f:
                        dataset: dict[str, Entry] = pickle.load(f)

                    dataset[self._timestamp] = {"data": data, "meta": meta}

                    with open(filename, "wb") as f:
                        pickle.dump(dataset, f)
            for chart in self._charts.values():
                chart.finalize()

            if not success:
                self._messenger.put("status", "stopped")
            else:
                self._messenger.put("status", "completed")
                return

        except asyncio.CancelledError:
            coros: list[CoroutineType[Any, Any, Any]] = []
            for saver in self._savers.values():
                coros.append(saver.kill())
            for chart in self._charts.values():
                coros.append(chart.kill())

            await asyncio.gather(*coros)
            self._cancelled.set()

    """Public Interface of self"""

    async def kill(self):
        if hasattr(self, "_runner_task"):
            # Cancel the task
            self._runner_task.cancel()
            await self._cancelled.wait()

        # Shutting down the queue shall close the websocket if there is one
        self._messenger.shutdown()

        for chart in self._charts.values():
            await chart.kill()

        # Still try to gracefully clean up savers as there may be important data
        for saver in self._savers.values():
            await saver.kill()

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

    def stop_async(self):
        self._should_stop.set()
        # Set the running event as well just in case it is being paused
        self._should_run.set()

    def pause_sync(self):
        self._should_run.clear()
        self._not_running.wait()
        self._messenger.put("status", "paused")

    def unpause(self):
        self._should_run.set()
        self._messenger.put("status", "continued")

    """Experiment Manager override"""

    @override
    def suggestTotalIterations(self, total_iterations: int):
        self._messenger.put("proposed_total_iterations", total_iterations)

    """Chart Manager override"""

    @override
    def createChart(self, chartT: _ChartABC, kwargs: Any = {}):
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
    def createSaver(self, saverT: type[_SaverABC], kwargs: Any = {}):
        title = kwargs["title"]

        self._savers[title] = SaverProxy(
            timestamp=self._timestamp,
            saverT=saverT,
            kwargs=kwargs,
        )

        return self._savers[title]._saver
