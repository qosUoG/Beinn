from abc import ABC, abstractmethod
from threading import Lock
from typing import Any, Callable

import numpy as np


class ChartABC(ABC):
    def __init__(self):
        self._lock = Lock()
        self._history = bytes()

        self._send: Callable[[bytes], None] | None = None

        self.title: str

    @abstractmethod
    def getConfig(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def plot(
        self, frame: dict[str, np.typing.NDArray[np.float64] | list[float]]
    ) -> None:
        """
        When implementing this method, one must call _plot to ensure the frame is actually stored
        """
        raise NotImplementedError

    def _plot(self, encoded: bytes) -> None:
        with self._lock:
            # Make sure to have a copy
            self._history += encoded

            if self._send is None:
                return

            self._send(encoded)

    def subscribe(self, send: Callable[[bytes], None]):
        # First yield frames available before subscription
        with self._lock:
            self._send = send
            if self._history:
                self._send(self._history)

    def unsubscribe(self):
        with self._lock:
            self._send = None
