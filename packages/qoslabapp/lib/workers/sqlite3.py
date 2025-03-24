import asyncio
import queue
from typing import Any, Literal
from aiosqlite import Connection, Cursor
import aiosqlite
from threading import Event, Thread
from time import sleep

from ..proxies.sql_saver import SqlSaverProxy


class _SqlRequest:
    def __init__(
        self, type: Literal["script"] | Literal["many"], sql: str, payload: Any = None
    ):
        self.type = type
        self.sql = sql
        self.payload = payload

        if self.type == "many":
            assert payload is not None
        elif self.type == "script":
            assert payload is None


# The worker shall run on main thread only
class SqlWorker:
    _queue: queue.Queue[_SqlRequest] = queue.Queue()
    _task: asyncio.Task

    @classmethod
    def start(cls):
        if not hasattr(cls, "_task"):
            cls._task = asyncio.create_task(cls.sqlWorker())

    @classmethod
    def queueScript(cls, sql: str):
        cls._queue.put(_SqlRequest(type="script", sql=sql))

    @classmethod
    def queueMany(cls, sql: str, payload: Any):
        cls._queue.put(_SqlRequest(type="script", sql=sql, payload=payload))

    @classmethod
    async def sqlWorker(cls):
        _sqlite3_connection = await aiosqlite.connect("data.db")
        _sqlite3_cursor = await _sqlite3_connection.cursor()
        while True:
            request = cls._queue.get()

            if request.type == "script":
                await _sqlite3_cursor.executescript(request.sql)
            elif request.type == "many":
                await _sqlite3_cursor.executemany(request.sql, request.payload)

            await _sqlite3_connection.commit()
