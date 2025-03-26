import asyncio
from typing import Iterable, Literal
import aiosqlite


class _Request:
    def __init__(
        self,
        *,
        type: Literal["script"]
        | Literal["many"]
        | Literal["stop"]
        | Literal["fetchall"],
        sql: str = None,
        payload: list = None,
    ):
        self.type = type
        self.sql = sql
        self.payload = payload
        self.executed = asyncio.Event()

        if self.type == "many":
            assert self.payload is not None
        else:
            assert self.payload is None

        # This is only used in "fetchall"
        self.value: Iterable[aiosqlite.Row]


class SqlWorker:
    _queue: asyncio.Queue[_Request] = asyncio.Queue()
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
        cls._queue.put_nowait(_Request(type="stop"))
        await cls._task_cancelled.wait()

    @classmethod
    def putScript(cls, sql: str):
        cls._queue.put_nowait(_Request(type="script", sql=sql))

    @classmethod
    def putMany(cls, sql: str, payload: list):
        cls._queue.put_nowait(_Request(type="many", sql=sql, payload=payload))

    @classmethod
    async def putFetchall(cls, sql: str):
        req = _Request(type="fetchall", sql=sql)
        cls._queue.put_nowait(req)
        await req.executed.wait()
        return req.value

    @classmethod
    async def sqlWorker(cls):
        try:
            cls._sqlite3_connection = await aiosqlite.connect("./data/data.db")
            cls._sqlite3_cursor = await cls._sqlite3_connection.cursor()
            while True:
                request = await cls._queue.get()

                if request.type == "stop":
                    await cls._sqlite3_connection.close()
                    cls._task_cancelled.set()
                    return

                elif request.type == "script":
                    await cls._sqlite3_cursor.executescript(request.sql)
                elif request.type == "many":
                    await cls._sqlite3_cursor.executemany(request.sql, request.payload)
                elif request.type == "fetchall":
                    res = await cls._sqlite3_cursor.execute(request.sql)
                    request.value = await res.fetchall()

                await cls._sqlite3_connection.commit()
                request.executed.set()

        except Exception as e:
            print("Exception in sqlWorker task in request:")
            print(request.type)
            print(request.sql)
            print(request.payload)
            print(e)
