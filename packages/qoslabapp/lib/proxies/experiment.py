import asyncio

import json
from threading import Event, Lock
from typing import Any, Callable


from qoslablib.exceptions import ExperimentEnded
from qoslablib.params import Params
from qoslablib.runtime import ExperimentABC

from qoslablib.runtime import ManagerABC

from ..utils import singleKVDictMessage, singleKVNumberMessage, singleKVStrMessage


# Experiment Messenger shall be instantiated in the main thread
class ExperimentMessenger:
    def __init__(self, loop: asyncio.EventLoop):
        self._loop = loop
        self._message_queue = asyncio.Queue()

    def getMessageQueueGetFn(self):
        # return a function that keeps yielding new event
        return self._message_queue.get

    def appendObjMessage(self, key: str, obj: dict[str, Any]):
        self._appendMessage(singleKVDictMessage(key, obj))

    def _appendMessage(self, message: str):
        self._message_queue.put_nowait(message)

    # This is meant to be consumed by functions calling from other threads
    def _threadSafeAppendMessage(self, message: str):
        self._loop.call_soon_threadsafe(lambda: self._appendMessage(message))

    # thread safe API
    def threadSafeSendStarted(self):
        self._threadSafeAppendMessage(singleKVStrMessage("status", "started"))

    def threadSafeSendStopped(self):
        self._threadSafeAppendMessage(singleKVStrMessage("status", "stopped"))

    def threadSafeSendPaused(self):
        self._threadSafeAppendMessage(singleKVStrMessage("status", "paused"))

    def threadSafeSendContinued(self):
        self._threadSafeAppendMessage(singleKVStrMessage("status", "continued"))

    def threadSafeSendCompleted(self):
        self._threadSafeAppendMessage(singleKVStrMessage("status", "completed"))

    def threadSafeSendLoopCount(self, loop_count: int):
        self._threadSafeAppendMessage(singleKVNumberMessage("loop_count", loop_count))

    def threadSafeSendProposedTotalLoop(self, proposed_total_loop: int):
        self._threadSafeAppendMessage(
            singleKVNumberMessage("proposed_total_loop", proposed_total_loop)
        )


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

        self._messenger = ExperimentMessenger(self.manager.loop)

        self._experiment_task: asyncio.Task

    def getMessageQueueGetFn(self):
        return self._messenger.getMessageQueueGetFn()

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

        self._messenger.threadSafeSendStopped()

    def pause(self):
        self._should_run.clear()
        self._loop_ended.wait()

        self._messenger.threadSafeSendPaused()

    def stopped(self):
        return self._stopped.is_set()

    def unpause(self):
        self._should_run.set()
        self._messenger.threadSafeSendContinued()

    # Following runner functions are only called in runner and must be thread safe
    def runner_shouldRun(self):
        return self._should_run.is_set()

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
        self._messenger.threadSafeSendLoopCount(self.loop_count)

    def runner_sendStartedMessage(self):
        self._messenger.threadSafeSendStarted()

    def runner_getMessengerAppendObjFn(self):
        return self._messenger.appendObjMessage

    def runner_completed(self):
        self._messenger.threadSafeSendCompleted()

    @property
    def proposed_total_loop(self):
        with self._proposed_total_loop_lock:
            return self._proposed_total_loop

    @proposed_total_loop.setter
    def proposed_total_loop(self, value: int):
        with self._proposed_total_loop_lock:
            self._proposed_total_loop = value

            # Post to event message queue
            self._messenger.threadSafeSendProposedTotalLoop(self._proposed_total_loop)


def _experiment_runner(proxy: ExperimentProxy):
    # Wait the running event set_ before initializing
    proxy.runner_waitUntilShouldRun()
    # First run the inialize method and get the number of loops
    proxy.proposed_total_loop = proxy._experiment.initialize(proxy.manager)

    # Then run the initializer of extensions from appstate
    proxy.manager.loop.call_soon_threadsafe(
        lambda: proxy.manager.initializeExtensions(
            proxy.experiment_id, proxy.runner_getMessengerAppendObjFn()
        )
    )

    # Post Start event to message queue
    proxy.runner_sendStartedMessage()

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

            if not proxy.runner_shouldRun():
                # Decrement to exclude the previous loop index
                proxy.loop_count -= 1

            proxy.runner_endLoop()

        except ExperimentEnded:
            print("experiment ended")
            proxy.runner_endLoop()
            proxy.runner_completed()

            return
