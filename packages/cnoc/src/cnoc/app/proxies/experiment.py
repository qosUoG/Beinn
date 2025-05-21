import asyncio
from multiprocessing import Process
from multiprocessing.managers import BaseManager
import os
import pickle
from multiprocessing import Event
import time
from types import CoroutineType
from typing import Any, Callable, TypedDict, cast, override


from ...public.exceptions import ExperimentEnded
from cnoc.extensions.chart import _ChartABC

from cnoc.extensions.saver import _SaverABC
from websockets import ServerConnection

from ...public.params import Params
from ...public.experiment import ExperimentABC
from ...public.managers import ManagerABC

from .chart import ChartProxy
from .saver import SaverProxy


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


class ExperimentProxy(ManagerABC):
    class _ExperimentRunner:
        def __init__(self, *, id: str, experiment_cls: type[ExperimentABC]):
            # Experiment Instance
            self.experiment_id = id
            self._experiment = experiment_cls()

            # Manager
            self._manager = _Manager(
                suggestTotalIterations=self._suggestTotalIterations,
                createChart=self._createChart,
                createSaver=self._createSaver,
            )

            # Extensions
            self._charts: dict[str, ChartProxy] = {}
            self._savers: dict[str, SaverProxy] = {}

            # signals
            self.running = Event()
            self.not_running = Event()
            self.should_run = Event()
            self.should_stop = Event()

            self._reset()

        def _reset(self):
            # Constant
            self._timestamp = int(time.time() * 1000)

            # Iteration vars
            self._iteration_count = -1

            # Signals
            self.running.clear()
            self.should_run.clear()
            self.should_stop.clear()
            self.not_running.clear()

            # Lifecycle hooks
            self.started_listeners: list[Callable[[], None]] = []
            self.paused_listeners: list[Callable[[], None]] = []
            self.stopped_listeners: list[Callable[[bool], None]] = []
            self.loop_start_listeners: list[Callable[[int], None]] = []
            self.loop_end_listeners: list[Callable[[int], None]] = []

        def run(self):
            try:
                """ STEP 0 """
                # Run setup fn
                self._experiment.setup(self._manager)

                # Execute listeners
                for started_listener in self.started_listeners:
                    started_listener()

                while True:
                    """ STEP 1.1 """
                    # Wait until the running event is set in each loop
                    self.should_run.wait()

                    """ STEP 1.2 """
                    # Stop the experiment if the stop event is set
                    if self._should_stop.is_set():
                        self._experiment.cleanup()

                        # Execute listeners
                        for stopped_listener in self.stopped_listeners:
                            stopped_listener(False)

                        return

                    """ STEP 1.3 """
                    # Loop the experiment once with the newest index
                    self.running.set()
                    self.not_running.clear()
                    try:
                        self._experiment.loop(self._iteration_count + 1)

                    except ExperimentEnded:
                        # flush stdout
                        print("", end="", flush=True)

                        self._iteration_count += 1
                        # Execute listeners
                        for loop_end_listener in self.loop_end_listeners:
                            loop_end_listener(self._iteration_count)

                        for stopped_listener in self.stopped_listeners:
                            stopped_listener(True)
                        return

                    """ STEP 1.4 """
                    # flush stdout
                    print("", end="", flush=True)

                    self.running.clear()
                    self.not_running.set()
                    if self.should_run.is_set():
                        # Increment only if it is not paused, i.e. it will redo the iteration after unpaused
                        self._iteration_count += 1
                        # Execute listeners
                        for loop_end_listener in self.loop_end_listeners:
                            loop_end_listener(self._iteration_count)

            except Exception as e:
                print("Exception in experiment runner", flush=True)
                print(e, flush=True)

                self._experiment.cleanup()
                # Execute listeners
                for stopped_listener in self.stopped_listeners:
                    stopped_listener(False)

                return

        # TODO
        @override
        def _suggestTotalIterations(self, total_iterations: int):
            self._messenger.put("proposed_total_iterations", total_iterations)

        """Chart Manager override"""

        # TODO
        @override
        def _createChart(self, chartT: _ChartABC, kwargs: Any = {}):
            title = kwargs["title"]

            self._charts[title] = ChartProxy(
                chartT=chartT,
                kwargs=kwargs,
            )

            self._messenger.put("chart_config", self._charts[title].getConfig())
            return self._charts[title]._chart

        """Public Interface to Chart"""

        # TODO
        def subscribeChart(self, title: str, ws: ServerConnection):
            return self._charts[title].subscribe(ws)

        """Sql Saver Manager override"""

        # TODO
        @override
        def _createSaver(self, saverT: type[_SaverABC], kwargs: Any = {}):
            title = kwargs["title"]

            self._savers[title] = SaverProxy(
                timestamp=self._timestamp,
                saverT=saverT,
                kwargs=kwargs,
            )

            return self._savers[title]._saver

    class _ExperimentProcessManager(BaseManager):
        pass

    _ExperimentProcessManager.register("ExperimentRunner", _ExperimentRunner)

    def __init__(
        self,
        *,
        id: str,
        experiment_cls: type[ExperimentABC],
    ):
        # Experiment Process
        self.experiment_id = id
        self._process_manager = ExperimentProxy._ExperimentProcessManager()
        self._experiment_runner = (
            cast(
                type[ExperimentProxy._ExperimentRunner],
                self._process_manager.ExperimentRunner,
            )
        )(id=id, experiment_cls=experiment_cls)

        # Extensions
        self._charts: dict[str, ChartProxy] = {}
        self._savers: dict[str, SaverProxy] = {}

    """
    Experiment lifecycle listeners
    """

    def onStarted(self, callback: Callable[[], None]):
        self._experiment_runner.started_listeners.append(callback)

    def onPaused(self, callback: Callable[[], None]):
        self._experiment_runner.paused_listeners.append(callback)

    def onStopped(self, callback: Callable[[bool], None]):
        self._experiment_runner.stopped_listeners.append(callback)

    def onLoopStart(self, callback: Callable[[int], None]):
        self._experiment_runner.loop_start_listeners.append(callback)

    def onLoopEnd(self, callback: Callable[[int], None]):
        self._experiment_runner.loop_end_listeners.append(callback)

    """
    Experiment lifecycle control
    
    Note that the target state is not waited before return. 
    i.e. pause would only change the state to pausing, instead of paused
    To listen to -ed event, append to the lifecycle listeners
    """

    async def start(self):
        if (
            hasattr(self, "_experiment_process")
            and self._experiment_process.exitcode is None
        ):
            self._experiment_process.kill()
            await asyncio.sleep(1000)

        # run the experiment
        self._experiment_process = Process(lambda: self._experiment_runner.run())
        self._experiment_process.run()

    def pause(self):
        self._experiment_runner.should_run.clear()

    def unpause(self):
        self._experiment_runner.should_run.set()

    def stop(self):
        self._experiment_runner.should_stop.set()
        # In case the experiment is paused
        self._experiment_runner.should_run.set()

    async def kill(self):
        if (
            hasattr(self, "_experiment_process")
            and self._experiment_process.exitcode is None
        ):
            self._experiment_process.kill()

        # TODO
        for chart in self._charts.values():
            await chart.kill()

        for saver in self._savers.values():
            await saver.kill()

    # TODO
    async def runner_thread_holder(self):
        try:
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

    """Public Interface to experiment"""

    @property
    def params(self):
        return self._experiment_runner._experiment.params

    @params.setter
    def params(self, params: Params):
        self._experiment_runner._experiment.params = params
