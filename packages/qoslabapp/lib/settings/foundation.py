import asyncio
from threading import Event
import time


class Foundation:
    _loop: asyncio.EventLoop

    @classmethod
    def getLoop(cls):
        return cls._loop

    @classmethod
    def setLoop(cls, loop: asyncio.EventLoop):
        cls._loop = loop


class ExperimentStatus:
    def __init__(self, params_backup: dict[str, dict[str, str]]):
        self.stopped = Event()
        self.success = Event()
        self.timestamp = int(time.time() * 1000)
        self.params_backup = params_backup
