import asyncio
from dataclasses import dataclass
from threading import Event, Lock
from typing import TypedDict

from qoslablib.exceptions import ExperimentEnded
from qoslablib.params import Params
from qoslablib.runtime import ExperimentABC

from qoslablib.runtime import HoldersABC


class Message(TypedDict):
    key: str
    value: str


@dataclass
class ExperimentProxy:
    def __init__(
        self, *, id: str, experimentCls: type[ExperimentABC], holder: type[HoldersABC]
    ):
        self.experiment_id = id
        self._experiment = experimentCls(holder)

    @property
    def params(self):
        return self._experiment.params

    @params.setter
    def params(self, params: Params):
        self._experiment.params = params

    # Loop Count
    # Setting to -1 makes it start looping at 0

    _loop_count_lock = Lock()
    _loop_count: int = -1

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

    _message_queue = list[Message]

    def appendMessage(self, message):
        self._message_queue.append(message)

    # These would be used with _expeirment_runner
    _running = Event()
    _should_run = Event()
    _should_stop = Event()
    _stopped = Event()
    _loop_ended = Event()

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

    loop_index_subscribers: list[Event] = []

    def end_loop(self):
        self._running.clear()
        self._loop_ended.set()
        for subscriber in self.loop_index_subscribers:
            subscriber.set()

    _proposed_total_loop_lock = Lock()
    _proposed_total_loop: int = 0

    @property
    def proposed_total_loop(self):
        with self._proposed_total_loop_lock:
            return self._proposed_total_loop

    @proposed_total_loop.setter
    def proposed_total_loop(self, value: int):
        with self._proposed_total_loop_lock:
            self._proposed_total_loop = value


def _experiment_runner(handler: ExperimentProxy):
    # Wait the running event set_ before initializing
    handler.waitUntilShouldRun()
    # First run the inialize _method and get the number of loops
    handler._experiment.initialize()

    while True:
        # Wait until the running event is set in each loop
        handler.waitUntilShouldRun()

        # Stop the _experiment is the stop event is set
        if handler.should_stop():
            handler._experiment.stop()
            handler.to_stopped()
            return

        handler.start_loop()

        # Loop the _experiment once with the newest index
        try:
            handler.loop_count += 1
            handler._experiment.loop(handler.loop_count)

            handler.end_loop()

        except ExperimentEnded:
            print("experiment ended")
            return
