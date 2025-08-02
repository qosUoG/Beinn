"""Base Class of Experiment, Experiment Manger

For examples of defining experiment class (scripts), please refer to examples in
example/examplelib.

    * Experiment - Base class of all experiment scripts
        Users shall define experiment scripts by using ExperimentABC as the base class.

"""

from abc import ABC, abstractmethod
import asyncio
from threading import Event
from time import time
from typing import Callable, Literal, TypedDict

from .charts._chart import ChartABC


class ExperimentCompleted(Exception):
    pass


class Listeners(TypedDict):
    expected_loop_count: list[Callable[[int], None]]

    started: list[Callable[[], None]]
    paused: list[Callable[[], None]]
    stopped: list[Callable[[], None]]
    completed: list[Callable[[], None]]

    loop_start: list[Callable[[int], None]]
    loop_end: list[Callable[[int], None]]

    chart_created: list[Callable[[dict], None]]


type ExperimentEvents = (
    Literal["expected_loop_count"]
    | Literal["started"]
    | Literal["paused"]
    | Literal["stopped"]
    | Literal["completed"]
    | Literal["loop_start"]
    | Literal["loop_end"]
    | Literal["chart_created"]
)


class ExperimentABC(ABC):
    """
    Base class of all experiment scripts

    Attributes
    ----------
    params : .params.Params
        a dictionary of parameters accessible by the experiment script

    """

    # Instance shall initiate params in __init__() function, as well as

    def __init__(self):
        """
        No parameters shall be passed to the __init__ function.

        Implementation of drivers shall also make sure to instantiate the
        self.params attribute as well.

         To be type safe, implementors may also define a params type specific
        to the experiment script. Detail please refer to example/experiment
        """

        from .params import Params

        self.params: Params

        self._cnoc_should_run = Event()
        self._cnoc_should_stop = Event()
        self._cnoc_loop_count_count = -1

        # Lifecycle hooks
        self._cnoc_listeners: Listeners = {
            "expected_loop_count": [],
            "started": [],
            "paused": [],
            "stopped": [],
            "completed": [],
            "loop_start": [],
            "loop_end": [],
            "chart_created": [],
        }

        # Charts
        self._cnoc_charts: dict[str, ChartABC] = []

    def _cnoc_on(self, event: ExperimentEvents, callback: Callable[[], None]):
        self._cnoc_listeners[event].append(callback)

    def _cnoc_pause(self):
        self._cnoc_should_run.clear()

    def _cnoc_continue(self):
        self._cnoc_should_run.set()

    def _cnoc_stop(self):
        self._cnoc_should_stop.set()
        self._cnoc_should_run.set()

    def _cnoc_start(self):
        # Make sure the experiment starts in a fresh state
        self._cnoc_loop_count_count = -1
        self._cnoc_should_run.clear()
        self._cnoc_should_stop.clear()

        self._timestamp = int(time() * 1000)

        self.start()

        for listener in self._cnoc_listeners["expected_loop_count"]:
            listener(
                self._cnoc_expected_loop_count
                if hasattr(self, "_cnoc_expected_loop_count")
                else -1
            )

        self._runner_task = asyncio.create_task(asyncio.to_thread(self._cnoc_runner))
        self._cnoc_should_run.set()

    def _cnoc_runner(self):
        try:
            for listener in self._cnoc_listeners["started"]:
                listener()

            while True:
                # Wait until the running event is set in each loop
                self._cnoc_should_run.wait()

                # Stop the experiment is the stop event is set
                if self._cnoc_should_stop.is_set():
                    # self._cnoc_experiment.cleanup()
                    self._cnoc_should_run.clear()

                    for listener in self._cnoc_listeners["stopped"]:
                        listener()

                    return

                # Loop the experiment once with the newest index

                # self._cnoc_not_running.clear()
                self._cnoc_loop_count_count += 1

                try:
                    for listener in self._cnoc_listeners["loop_start"]:
                        listener(self._cnoc_loop_count_count)

                    self.loop(self._cnoc_loop_count_count)
                    # flush stdout
                    print("", end="", flush=True)

                except ExperimentCompleted:
                    if (
                        not self._cnoc_should_stop.is_set()
                        and self._cnoc_should_run.is_set()
                    ):
                        print("Experiment completed", flush=True)

                        for listener in self._cnoc_listeners["loop_end"]:
                            listener(self._cnoc_loop_count_count)

                        # Run all stop listeners
                        for listener in self._cnoc_listeners["completed"]:
                            listener()

                        # Signal the charts to stop
                        for chart in self._cnoc_charts.values():
                            chart._cnoc_stopChart()
                        return

                # we want to pause
                if not self._cnoc_should_run.is_set():
                    # Decrement to exclude the previous loop index
                    self._cnoc_loop_count_count -= 1
                    for listener in self._cnoc_listeners["paused"]:
                        listener()
                    continue

                # self._cnoc_not_running.set()

                for listener in self._cnoc_listeners["loop_end"]:
                    listener(self._cnoc_loop_count_count)

        except Exception as e:
            print(f"Exception in experiment: {e}", flush=True)
            return

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def loop(self, index: int) -> None:
        raise NotImplementedError

    def cleanup(self) -> None:
        """
        Perform any clean up if needed

        This method would run once after the loop method is no longer iterating. Users may perform
        any clean up in this method. However, please be aware other experiment script may still be running

        It is optional to implement this method.
        """
        pass

    def cnocCreateChart(self, chart: ChartABC):
        self._cnoc_charts[chart.title] = chart
        for listener in self._cnoc_listeners["chart_created"]:
            listener(chart.getConfig())

    def cnocExpectedLoopCount(self, loop_count: int):
        self._cnoc_expected_loop_count = loop_count
