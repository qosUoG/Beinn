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
    _queue: asyncio.Queue[_SqlRequest] = asyncio.Queue()
    _task: asyncio.Task

    _sqlite3_connection: aiosqlite.Connection
    _sqlite3_cursor: aiosqlite.Cursor

    _task_cancelled = asyncio.Event()
    _task_should_cancel = asyncio.Event()

    @classmethod
    def start(cls):
        if not hasattr(cls, "_task"):
            cls._task = asyncio.create_task(cls.sqlWorker())

    @classmethod
    async def stop(cls):
        if not hasattr(cls, "_task"):
            return

        cls._task_should_cancel.set()
        await cls._task_cancelled.wait()

    @classmethod
    def queueScript(cls, sql: str):
        cls._queue.put_nowait(_SqlRequest(type="script", sql=sql))

    @classmethod
    def queueMany(cls, sql: str, payload: Any):
        cls._queue.put_nowait(_SqlRequest(type="script", sql=sql, payload=payload))

    @classmethod
    async def sqlWorker(cls):
        cls._sqlite3_connection = await aiosqlite.connect("data.db")
        cls._sqlite3_cursor = await cls._sqlite3_connection.cursor()
        while True:
            request = await cls._queue.get()

            if cls._task_should_cancel.is_set():
                await cls._sqlite3_connection.close()
                cls._task_cancelled.set()
                return

            if request.type == "script":
                await cls._sqlite3_cursor.executescript(request.sql)
            elif request.type == "many":
                await cls._sqlite3_cursor.executemany(request.sql, request.payload)

            await cls._sqlite3_connection.commit()
