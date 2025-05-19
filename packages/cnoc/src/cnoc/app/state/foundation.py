import asyncio
from asyncio import Event
import threading
import time
from typing import Any, Coroutine


class Foundation:
    _loop: asyncio.EventLoop
    _tasks: list[asyncio.Task]

    @classmethod
    def crateTask(cls, coro: Coroutine[Any, Any, Any]):
        cls._tasks.append(asyncio.create_task(coro))

    @classmethod
    def getLoop(cls):
        return cls._loop

    @classmethod
    def setLoop(cls, loop: asyncio.EventLoop):
        cls._loop = loop

    @classmethod
    def runCoroThreadsafeBlocking(cls, coro: Coroutine[Any, Any, None]):
        done = threading.Event()

        async def _inner():
            await coro
            done.set()

        asyncio.create_task(_inner())
        done.wait()


class ExperimentStatus:
    def __init__(self, params_backup: dict[str, dict[str, str]]):
        self.stopped = Event()
        self.success = Event()
        self.timestamp = int(time.time() * 1000)
        self.params_backup = params_backup
