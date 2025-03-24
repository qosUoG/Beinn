import asyncio
from typing import Any, Literal
from aiosqlite import Connection, Cursor
import aiosqlite
from threading import Event
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
    _sqlite3_connection: Connection
    _sqlite3_cursor: Cursor

    _queue: asyncio.Queue[_SqlRequest] = asyncio.Queue()
    _task: asyncio.Task

    @classmethod
    def subscribe(cls):
        if not hasattr(cls, "_sqlite3_connection"):
            asyncio.create_task(cls._start())

        # Return the functions they can interact with
        return (cls.queueScript, cls.queueMany)

    @classmethod
    async def _start(cls):
        # Create connection and start the worker if haven't
        if not hasattr(cls, "_sqlite3_connection"):
            cls._sqlite3_connection = await aiosqlite.connect("data.db")
            cls._sqlite3_cursor = await cls._sqlite3_connection.cursor()
            cls._task = asyncio.create_task(cls.sqlWorker())

    @classmethod
    def queueScript(cls, sql: str):
        asyncio.create_task(cls._queueScript(sql))

    @classmethod
    async def _queueScript(cls, sql: str):
        await cls._queue.put(_SqlRequest(type="script", sql=sql))

    @classmethod
    def queueMany(cls, sql: str, payload: Any):
        asyncio.create_task(cls._queueMany(sql, payload))

    @classmethod
    async def _queueMany(cls, sql: str, payload: Any):
        await cls._queue.put(_SqlRequest(type="script", sql=sql, payload=payload))

    @classmethod
    async def sqlWorker(cls):
        while True:
            request = await cls._queue.get()

            if request.type == "script":
                await cls._sqlite3_cursor.executescript(request.sql)
            elif request.type == "many":
                await cls._sqlite3_cursor.executemany(request.sql, request.payload)

            await cls._sqlite3_connection.commit()
