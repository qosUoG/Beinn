import asyncio

from threading import Event, Lock


from qoslablib.exceptions import ExperimentEnded
from qoslablib.params import Params
from qoslablib.runtime import ExperimentABC

from qoslablib.runtime import ManagerABC

from ..utils import singleKVNumberMessage, singleKVStrMessage


class ExperimentProxy:
    def __init__(
        self,
        *,
        id: str,
        experimentCls: type[ExperimentABC],
        manager: type[ManagerABC],
    ):
        self.experiment_id = id
        self._experiment = experimentCls()

        self.manager = manager

        # Loop Count
        # Setting to -1 makes it start looping at 0

        self._loop_count_lock = Lock()
        self._loop_count: int = -1

        # These would be used with _expeirment_runner
        self._running = Event()
        self._should_run = Event()
        self._should_stop = Event()
        self._stopped = Event()
        self._loop_ended = Event()

        self._proposed_total_loop_lock = Lock()
        self._proposed_total_loop: int = 0

        self._message_queue = asyncio.Queue()

        self._experiment_task: asyncio.Task

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

    def getMessageQueueFn(self):
        # return a function that keeps yielding new event
        return self._message_queue.get

    def appendMessage(self, message: str):
        self._message_queue.put_nowait(message)

    def threadSafeAppendMessage(self, message: str):
        self.manager.loop.call_soon_threadsafe(lambda: self.appendMessage(message))

    def start(self):
        # Make sure experiment is at fresh state
        self.loop_count = -1

        # Reset All Events
        self._running = Event()
        self._should_run = Event()
        self._should_stop = Event()
        self._stopped = Event()
        self._loop_ended = Event()

        self._experiment_task = asyncio.create_task(
            asyncio.to_thread(_experiment_runner, self)
        )

        # run the experiment!
        self._should_run.set()

    def cancelExperimentTask(self):
        self.stop()
        self._experiment_task.cancel()

    def stop(self):
        self._should_stop.set()
        # Set the running event as well just in case it is being paused
        self._should_run.set()
        # Wait till it actually stopped
        self._stopped.wait()

        self.appendMessage(singleKVStrMessage("status", "stopped"))

    def pause(self):
        self._should_run.clear()
        self._loop_ended.wait()
        self.appendMessage(singleKVStrMessage("status", "paused"))

    def stopped(self):
        return self._stopped.is_set()

    def unpause(self):
        self._should_run.set()
        self.appendMessage(singleKVStrMessage("status", "continued"))

    # Following runner functions are only called in runner and must be thread safe

    def runner_shouldStop(self):
        return self._should_stop.is_set()

    def runner_toStopped(self):
        self._should_run.clear()
        self._stopped.set()

    def runner_waitUntilShouldRun(self):
        self._should_run.wait()

    def runner_startLoop(self):
        self._running.set()
        self._loop_ended.clear()

    def runner_endLoop(self):
        self._running.clear()
        self._loop_ended.set()

        # Post loop count event to message queue
        with self._loop_count_lock:
            self.threadSafeAppendMessage(
                singleKVNumberMessage("loop_count", self._loop_count)
            )

    def runner_completed(self):
        self.threadSafeAppendMessage(singleKVStrMessage("status", "completed"))

    @property
    def proposed_total_loop(self):
        with self._proposed_total_loop_lock:
            return self._proposed_total_loop

    @proposed_total_loop.setter
    def proposed_total_loop(self, value: int):
        with self._proposed_total_loop_lock:
            self._proposed_total_loop = value

            # Post to event message queue
            self.threadSafeAppendMessage(
                singleKVNumberMessage("proposed_total_loop", self._proposed_total_loop)
            )


def _experiment_runner(proxy: ExperimentProxy):
    # Wait the running event set_ before initializing
    proxy.runner_waitUntilShouldRun()
    # First run the inialize method and get the number of loops
    proxy.proposed_total_loop = proxy._experiment.initialize(proxy.manager)

    # Then run the initializer of extensions from appstate
    proxy.manager.loop.call_soon_threadsafe(
        lambda: proxy.manager.initializeExtensions(proxy.experiment_id)
    )

    # Post Start event to message queue
    proxy.threadSafeAppendMessage(singleKVStrMessage("status", "started"))

    while True:
        # Wait until the running event is set in each loop
        proxy.runner_waitUntilShouldRun()

        # Stop the _experiment is the stop event is set
        if proxy.runner_shouldStop():
            proxy._experiment.stop()
            proxy.runner_toStopped()
            return

        proxy.runner_startLoop()

        # Loop the _experiment once with the newest index
        try:
            proxy.loop_count += 1
            proxy._experiment.loop(proxy.loop_count)

            proxy.runner_endLoop()

        except ExperimentEnded:
            print("experiment ended")
            proxy.runner_endLoop()
            proxy.runner_completed()

            return
