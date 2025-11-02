from abc import ABC, abstractmethod
import asyncio
from threading import Lock
from typing import Any


class ChartABC(ABC):
    def __init__(self):
        self._buf = bytes()
        self._history = bytes()

        self._lock = Lock()

        self._has_data = asyncio.Event()
        self._subscribed = False
        self._should_stop = False

        self.title: str

    @abstractmethod
    def getConfig(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def plot(self, frame: dict[str, float]):
        """
        When implementing this method, one must call _plot to ensure the frame is actually stored
        """
        raise NotImplementedError

    def _plot(self, encoded: bytes) -> None:
        with self._lock:
            # Make sure to have a copy
            self._history += encoded

            if self._subscribed:
                self._buf = encoded
                self._has_data.set()

    def stop(self):
        with self._lock:
            self._has_data.set()
            self._should_stop = True

    async def subscribe(self):
        # First yield frames available before subscription
        history: bytes = bytes()
        with self._lock:
            self._subscribed = True
            if self._history:
                history = self._history
        if history:
            yield history

        res: bytes = bytes()
        while True:
            await self._has_data.wait()

            with self._lock:
                if self._should_stop:
                    self._subscribed = False
                    return

                res = self._buf
                self._buf = bytes()
                self._has_data.clear()
            if res:
                yield res

    def unsubscribe(self):
        self._has_data.clear()
        self._subscribed = False
