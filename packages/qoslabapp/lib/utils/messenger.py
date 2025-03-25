import asyncio
from functools import singledispatchmethod
import json
from typing import Any


class Messenger:
    def __init__(self, loop: asyncio.EventLoop):
        self._loop = loop
        self._message_queue = asyncio.Queue[str]()

    async def get(self):
        # Return a single item
        return await self._message_queue.get()

    def _put_nowait(self, message: str):
        self._message_queue.put_nowait(message)

    @singledispatchmethod
    def put(self, key: str, value: str):
        self._put_nowait("{" + f'"key": "{key}", "value": "{value}"' + "}")

    @put.register
    def _(self, key: str, value: float | int):
        self._put_nowait("{" + f'"key": "{key}", "value": {value}' + "}")

    @put.register
    def _(self, key: str, value: dict[str, Any]):
        self._put_nowait(json.dumps({"key": key, "value": value}))

    # Thread safe versions
    @singledispatchmethod
    def put_threadsafe(self, key: str, value: str):
        self._loop.call_soon_threadsafe(
            lambda: self._put_nowait("{" + f'"key": "{key}", "value": "{value}"' + "}")
        )

    @put_threadsafe.register
    def _(self, key: str, value: float | int):
        self._loop.call_soon_threadsafe(
            lambda: self._put_nowait("{" + f'"key": "{key}", "value": {value}' + "}")
        )

    @put_threadsafe.register
    def _(self, key: str, value: dict[str, Any]):
        self._loop.call_soon_threadsafe(
            lambda: self._put_nowait(json.dumps({"key": key, "value": value}))
        )
