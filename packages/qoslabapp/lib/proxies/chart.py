import asyncio

from threading import Lock
from typing import Any

from fastapi import WebSocket

from qoslablib.extensions.chart import ChartABC


class ChartProxy:
    def __init__(
        self, *, experiment_id: str, title: str, chartT: type[ChartABC], kwargs: Any
    ):
        # Identifier of the chart handler
        self.title = title
        self.experiment_id = experiment_id

        # underlying chart instance
        self._chart = chartT(self._plot_fn, **kwargs)
        self._subscribers: list[ChartProxy.Subscriber] = []

        self._frames_history = bytes()
        self._frames_history_lock = Lock()

    def getConfig(self):
        return self._chart.config.toDict()

    # For posting to the frontend TODO Should not be here

    class Subscriber:
        def __init__(self):
            self.rate = 10
            self._active_frames_lock = Lock()
            self._active_frames = bytes()

        def toOwnedFrames(self):
            with self._active_frames_lock:
                if self._active_frames == bytes():
                    return None

                frames = self._active_frames
                self._active_frames = bytes()
                return frames

        def appendFrame(self, frame: bytes):
            with self._active_frames_lock:
                self._active_frames += frame

    def subscribe(self):
        frames_history: bytes
        subscriber: ChartProxy.Subscriber

        # Shares the frames history lock such that make sure the subscriber gets a history right at the moment of creation, such that
        with self._frames_history_lock:
            frames_history = self._frames_history
            subscriber = ChartProxy.Subscriber()
            self._subscribers.append(subscriber)

        # Function that yield frames according to the rate
        async def subscription():
            # First yield frames available before subscription
            if frames_history:
                yield frames_history

            while True:
                await asyncio.sleep(1 / subscriber.rate)
                frames = subscriber.toOwnedFrames()
                if frames is not None:
                    yield frames

        def unsubscribe():
            self._subscribers.remove(subscriber)

        def setRate(rate: int):
            subscriber.rate = rate

        return (subscription, unsubscribe, setRate)

    def _plot_fn(self, frame: bytes):
        with self._frames_history_lock:
            # Make sure to have a copy
            self._frames_history += frame
            # subscriber and frames history shares a lock such that the history is fetched at the same time as the subscriber list is modified
            for subscriber in self._subscribers:
                subscriber.appendFrame(frame)
