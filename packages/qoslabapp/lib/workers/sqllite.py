import asyncio
from typing import Literal
import aiosqlite


class Request:
    def __init__(
        self,
        type: Literal["script"] | Literal["many"] | Literal["stop"],
        sql: str = None,
        payload: list = None,
    ):
        self.type = type
        self.sql = sql
        self.payload = payload

        if self.type == "many":
            assert payload is not None
        else:
            assert payload is None


class SqlWorker:
    _queue: asyncio.Queue[Request] = asyncio.Queue()
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
        cls._queue.put_nowait(Request(type="stop"))
        await cls._task_cancelled.wait()

    @classmethod
    def putScript(cls, sql: str):
        cls._queue.put_nowait(Request(type="script", sql=sql))

    @classmethod
    def putMany(cls, sql: str, payload: list):
        cls._queue.put_nowait(Request(type="many", sql=sql, payload=payload))

    @classmethod
    async def sqlWorker(cls):
        try:
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

        except Exception as e:
            print("Exception in sqlWorker task")
            print(e)
