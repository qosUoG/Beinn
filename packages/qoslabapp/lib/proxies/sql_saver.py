import asyncio
from functools import singledispatchmethod
from threading import Lock
import time
from typing import Any, Literal

import aiosqlite
from qoslablib.extensions.saver import SqlSaverABC


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


class SqlWorker:
    _queue: asyncio.Queue[_SqlRequest] = asyncio.Queue()
    _task: asyncio.Task

    _sqlite3_connection: aiosqlite.Connection
    _sqlite3_cursor: aiosqlite.Cursor

    _task_cancelled = asyncio.Event()

    @classmethod
    def start(cls):
        if not hasattr(cls, "_task"):
            cls._task = asyncio.create_task(cls.sqlWorker())

    @classmethod
    async def stop(cls):
        if not hasattr(cls, "_task"):
            return

        # Anything put after the stop is lost
        cls._queue.put_nowait({"type": "stop"})
        await cls._task_cancelled.wait()

    @singledispatchmethod
    @classmethod
    def put(cls, sql: str):
        cls._queue.put_nowait(_SqlRequest(type="script", sql=sql))

    @put.register
    @classmethod
    def _(cls, sql: str, payload: Any):
        cls._queue.put_nowait(_SqlRequest(type="many", sql=sql, payload=payload))

    @classmethod
    async def sqlWorker(cls):
        cls._sqlite3_connection = await aiosqlite.connect("data.db")
        cls._sqlite3_cursor = await cls._sqlite3_connection.cursor()
        while True:
            request = await cls._queue.get()

            if request.type == "stop":
                await cls._sqlite3_connection.close()
                cls._task_cancelled.set()
                return

            if request.type == "script":
                await cls._sqlite3_cursor.executescript(request.sql)
            elif request.type == "many":
                await cls._sqlite3_cursor.executemany(request.sql, request.payload)

            await cls._sqlite3_connection.commit()


class SqlSaverProxy:
    def __init__(
        self,
        *,
        sql_saverT: type[SqlSaverABC],
        kwargs: Any,
    ):
        # sql_saver instance for consumer of sql_saver
        self._sql_saver = sql_saverT(save_fn=self._save_fn, **kwargs)

        self._frames_lock = Lock()
        self._frames: list[Any] = []

        table_name = (
            f"{self._sql_saver.config.title} timestamp:{int(time.time() * 1000)}"
        )
        create_table_sql = self._sql_saver.getCreateTableSql(table_name)
        self._insert_sql = self._sql_saver.getInsertSql(table_name)

        self._task: asyncio.Task

        self._should_cancel = asyncio.Event()
        self._stopped = asyncio.Event()

        # Start the worker
        SqlWorker.start()

        # Create the table
        SqlWorker.put(create_table_sql)

        # Create the task that continuously submit put request for registering frames
        self._task = asyncio.create_task(self._worker())

    """Public Interface"""

    def getConfig(self):
        return self._sql_saver.config.toDict()

    async def cleanup(self):
        # Cancel the task
        self._should_cancel.set()
        await self._stopped.wait()

    """Private task to continuously submit frames to worker"""

    async def _worker(self):
        while not self._should_cancel.is_set():
            await asyncio.sleep(2)
            self._flushFrames()

        # flush the frames one last time
        self._flushFrames()
        self._stopped.set()
        return

    def _flushFrames(self):
        frames = self._toOwnedFrames()
        if frames:
            SqlWorker.put(self._insert_sql, frames)

    def _toOwnedFrames(self):
        with self._frames_lock:
            frames = self._frames
            self._frames = []
            return frames

    """_save_fn to be used by underlying saver"""

    def _save_fn(self, frame: Any):
        with self._frames_lock:
            self._frames.append(frame)
