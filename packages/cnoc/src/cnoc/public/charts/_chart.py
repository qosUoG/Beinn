from abc import ABC, abstractmethod
import asyncio
from threading import Event, Lock
from typing import Any

from websockets import ServerConnection


class ChartBuf:
    def __init__(self):
        self.rate = 10
        self._lock = Lock()
        self._frames = bytes()

    def toOwnedFrames(self):
        with self._lock:
            frames = self._frames
            self._frames = bytes()
            return frames

    def appendFrame(self, frame: bytes):
        with self._lock:
            self._frames += frame


class ChartABC(ABC):
    def __init__(self):
        self._cnoc_bufs: dict[ServerConnection, ChartBuf] = []
        self._cnoc_history = bytes()
        self._cnoc_lock = Lock()
        self._cnoc_should_stop = Event()
        self._frames_history = bytes()

    def _cnoc_stopChart(self):
        self._cnoc_should_stop.set()

    def _cnoc_subscribe(self, ws: ServerConnection):
        self._cnoc_bufs[ws] = ChartBuf()

        # Shares the frames history lock such that make sure the buf gets a history right at the moment of creation, such that
        with self._cnoc_lock:
            frames_history = self._frames_history
            buf = ChartBuf()
            self._cnoc_bufs[ws] = buf

        async def subscription():
            # First yield frames available before subscription
            if frames_history:
                yield frames_history

            while True:
                await asyncio.sleep(1 / buf.rate)
                yield buf.toOwnedFrames()

                if self._cnoc_should_stop.is_set():
                    break

            # Flush remaining frames
            yield buf.toOwnedFrames()

        def unsubscribe():
            del self._cnoc_bufs[ws]

        def setRate(rate: int):
            self._cnoc_bufs[ws].rate = rate

        def getRate():
            return self._cnoc_bufs[ws].rate

        return (subscription, unsubscribe, setRate, getRate)

    @abstractmethod
    def getConfig(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def plot(self, frame: dict[str, float]):
        """
        When implementing this method, one must call _abc_plot to ensure the frame is actually stored
        """
        raise NotImplementedError

    def _cnoc_plot(self, encoded: bytes) -> None:
        with self._cnoc_lock:
            # Make sure to have a copy
            self._frames_history += encoded
            # buf and frames history shares a lock such that the history is fetched at the same time as the buf list is modified
            for buf in self._cnoc_bufs.values():
                buf.appendFrame(encoded)
