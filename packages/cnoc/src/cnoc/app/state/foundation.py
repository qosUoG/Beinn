import asyncio
from asyncio import Event
import time
from typing import Any, Coroutine

from websockets import ServerConnection


class Foundation:
    _loop: asyncio.EventLoop
    task: asyncio.Task[Any]
    workspace_ws: ServerConnection

    @classmethod
    def getLoop(cls):
        return cls._loop

    @classmethod
    def setLoop(cls, loop: asyncio.EventLoop):
        cls._loop = loop

    @classmethod
    def runCoroThreadsafeBlocking(cls, coro: Coroutine[Any, Any, None]):
        asyncio.run_coroutine_threadsafe(coro, cls._loop)


class ExperimentStatus:
    def __init__(self, params_backup: dict[str, dict[str, str]]):
        self.stopped = Event()
        self.success = Event()
        self.timestamp = int(time.time() * 1000)
        self.params_backup = params_backup
