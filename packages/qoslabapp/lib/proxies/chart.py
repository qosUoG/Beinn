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
        self.chart = chartT(
            initialize_fn=self._initialize_fn, plot_fn=self._plot_fn, **kwargs
        )
        self.connections: list[ChartProxy.Subscriber] = []

    def _initialize_fn(self):
        pass

    # For posting to the frontend TODO Should not be here

    class Subscriber:
        def __init__(self, ws: WebSocket):
            self.rate = 1
            self.ws: WebSocket

            self._frame_lock = Lock()
            self._frames: list[Any] = []

        def toOwnedFrames(self):
            with self._frame_lock:
                frames = self._frames
                self._frames = []
                return frames

        def appendFrame(self, frame: Any):
            with self._frame_lock:
                self._frames.append(frame)

    def subscribe(self, ws: WebSocket):
        subscriber = ChartProxy.Subscriber(ws)
        self.connections.append(subscriber)

        # Function that yield frames according to the rate
        async def subscription():
            await asyncio.sleep(1 / subscriber.rate)
            yield subscriber.toOwnedFrames()

        return subscription

    def _plot_fn(self, frame: Any):
        for subscriber in self.connections:
            subscriber.appendFrame(frame)
