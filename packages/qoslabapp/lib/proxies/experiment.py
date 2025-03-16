import asyncio

from threading import Event, Lock
from typing import TypedDict

from qoslablib.exceptions import ExperimentEnded
from qoslablib.params import Params
from qoslablib.runtime import ExperimentABC

from qoslablib.runtime import ManagerABC


class Message(TypedDict):
    key: str
    value: str


class ExperimentProxy:
    def __init__(
        self,
        *,
        id: str,
        experimentCls: type[ExperimentABC],
        manager: type[ManagerABC],
        loop: asyncio.EventLoop,
    ):
        self.experiment_id = id
        self._experiment = experimentCls()

        self.manager = manager

        # Loop Count
        # Setting to -1 makes it start looping at 0

        self._loop_count_lock = Lock()
        self._loop_count: int = -1

        self._message_queue: list[Message] = []

        # These would be used with _expeirment_runner
        self._running = Event()
        self._should_run = Event()
        self._should_stop = Event()
        self._stopped = Event()
        self._loop_ended = Event()

        self._proposed_total_loop_lock = Lock()
        self._proposed_total_loop: int = 0

        self.loop_index_subscribers: list[Event] = []

        self.loop = loop

    @property
    def params(self):
        return self._experiment.params

    @params.setter
    def params(self, params: Params):
        self._experiment.params = params

    @property
    def loop_count(self):
        with self._loop_count_lock:
            return self._loop_count

    @loop_count.setter
    def loop_count(self, value: int):
        with self._loop_count_lock:
            self._loop_count = value

    def getStreamingLoopCount(self):
        # return a function that yields new loop index when done
        event = Event()
        self.loop_index_subscribers.append(event)

        def yieldLoopIndex():
            # yield the current index first

            yield self.loop_count

            while True:
                event.wait()
                event.clear()
                yield self.loop_count

        return yieldLoopIndex

    def appendMessage(self, message):
        self._message_queue.append(message)

    _experiment_task: asyncio.Task

    def start(self):
        self._experiment_task = asyncio.create_task(
            asyncio.to_thread(
                _experiment_runner,
                args=(self),
            )
        )

        # run the experiment!
        self._should_run.set()

    def stop(self):
        self._should_stop.set()
        # Set the running event as well just in case it is being paused
        self._should_run.set()
        # Wait till it actually stopped
        self._stopped.wait()

    def pause(self):
        self._should_run.clear()
        self._loop_ended.wait()

    def unpause(self):
        self._should_run.set()

    def should_stop(self):
        return self._should_stop.is_set()

    def to_stopped(self):
        self._should_run.clear()
        self._stopped.set()

    def stopped(self):
        return self._stopped.is_set()

    def waitUntilShouldRun(self):
        self._should_run.wait()

    def start_loop(self):
        self._running.set()
        self._loop_ended.clear()

    def end_loop(self):
        self._running.clear()
        self._loop_ended.set()
        for subscriber in self.loop_index_subscribers:
            subscriber.set()

    @property
    def proposed_total_loop(self):
        with self._proposed_total_loop_lock:
            return self._proposed_total_loop

    @proposed_total_loop.setter
    def proposed_total_loop(self, value: int):
        with self._proposed_total_loop_lock:
            self._proposed_total_loop = value


def _experiment_runner(proxy: ExperimentProxy):
    # Wait the running event set_ before initializing
    proxy.waitUntilShouldRun()
    # First run the inialize method and get the number of loops
    proxy.proposed_total_loop = proxy._experiment.initialize(proxy.manager)

    # Then run the initializer of extensions from appstate
    proxy.loop.call_soon_threadsafe(
        proxy.manager.initializeExtensions(proxy.experiment_id)
    )

    while True:
        # Wait until the running event is set in each loop
        proxy.waitUntilShouldRun()

        # Stop the _experiment is the stop event is set
        if proxy.should_stop():
            proxy._experiment.stop()
            proxy.to_stopped()
            return

        proxy.start_loop()

        # Loop the _experiment once with the newest index
        try:
            proxy.loop_count += 1
            proxy._experiment.loop(proxy.loop_count)

            proxy.end_loop()

        except ExperimentEnded:
            print("experiment ended")
            return
