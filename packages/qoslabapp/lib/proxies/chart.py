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

    def initialize(self):
        pass

    def getConfig(self):
        return self._chart.config.toDict()

    # For posting to the frontend TODO Should not be here

    class Subscriber:
        def __init__(self):
            self.rate = 1
            self._frame_lock = Lock()
            self._frames: bytes = bytes()

        def toOwnedFrames(self):
            with self._frame_lock:
                if self._frames == bytes():
                    return None

                frames = self._frames
                self._frames = bytes()
                return frames

        def appendFrame(self, frame: bytes):
            with self._frame_lock:
                self._frames += frame

    def subscribe(self):
        subscriber = ChartProxy.Subscriber()
        self._subscribers.append(subscriber)

        # Function that yield frames according to the rate
        async def subscription():
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
        for subscriber in self._subscribers:
            subscriber.appendFrame(frame)
