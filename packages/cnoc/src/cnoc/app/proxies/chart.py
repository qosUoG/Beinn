import asyncio
from threading import Lock
import threading
from types import CoroutineType
from typing import Any

from cnoc.extensions.chart import _ChartABC
from websockets import ServerConnection


class _Subscriber:
    def __init__(self):
        self._rate = 10
        self._active_frames_lock = Lock()
        self._active_frames = bytes()

    def toOwnedFrames(self):
        with self._active_frames_lock:
            frames = self._active_frames
            self._active_frames = bytes()
            return frames

    def appendFrame(self, frame: bytes):
        with self._active_frames_lock:
            self._active_frames += frame

    def setRate(self, rate: int):
        self._rate = rate

    def getRate(self):
        return self._rate


class ChartProxy:
    def __init__(self, *, chartT: type[_ChartABC], kwargs: Any):
        # underlying chart instance
        self._chart = chartT(self._plot_fn, **kwargs)
        self._subscribers: dict[ServerConnection, _Subscriber] = {}

        # Lock synchronizing frame history and subscriber creation
        self._frames_history = bytes()

        self._tick_lock = Lock()

        self._experiment_stopped = threading.Event()

    """Public Interface towards ExperimentProxy"""

    def getConfig(self):
        return self._chart.config.toDict()

    def getChart(self):
        return self._chart

    # Hook when experiment ended
    def finalize(self):
        self._experiment_stopped.set()

    async def kill(self):
        # Close all ws connetions
        # Chart is not gracefully shut down as data is ephemeral anyways
        coros: list[CoroutineType[Any, Any, None]] = []
        for ws in self._subscribers.keys():
            coros.append(ws.close(code=4000))

        return asyncio.gather(*coros)

    """Public Interface for frontend Websocket control"""

    def subscribe(self, ws: ServerConnection):
        frames_history: bytes
        subscriber: _Subscriber

        # Shares the frames history lock such that make sure the subscriber gets a history right at the moment of creation, such that
        with self._tick_lock:
            frames_history = self._frames_history
            subscriber = _Subscriber()
            self._subscribers[ws] = subscriber

        # Function that yield frames according to the rate
        async def subscription():
            # First yield frames available before subscription
            if frames_history:
                yield frames_history

            while True:
                await asyncio.sleep(1 / subscriber.getRate())
                yield subscriber.toOwnedFrames()

                if self._experiment_stopped.is_set():
                    break

            # Flush remaining frames
            yield subscriber.toOwnedFrames()

        def unsubscribe():
            del self._subscribers[ws]

        def setRate(rate: int):
            self._subscribers[ws].setRate(rate)

        return (subscription, unsubscribe, setRate)

    """_plot_fn to be used by underlying chart"""

    def _plot_fn(self, frame: bytes):
        with self._tick_lock:
            # Make sure to have a copy
            self._frames_history += frame
            # subscriber and frames history shares a lock such that the history is fetched at the same time as the subscriber list is modified
            for subscriber in self._subscribers.values():
                subscriber.appendFrame(frame)
