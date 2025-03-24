import asyncio
from threading import Lock
import time
from types import CoroutineType
from typing import Any, Callable

from qoslablib.extensions.saver import SqlSaverABC


class SqlSaverProxy:
    def __init__(
        self,
        *,
        experiment_id: str,
        title: str,
        sql_saverT: type[SqlSaverABC],
        kwargs: Any,
    ):
        # Identifier for the sql saver handler
        self.title = title
        self.timestamp = int(time.time() * 1000)
        self.experiment_id = experiment_id

        # sql_saver instance for consumer of sql_saver
        self._sql_saver = sql_saverT(save_fn=self._save_fn, **kwargs)

        self._frame_lock = Lock()
        self._frames: list[Any] = []

        self._table_name = f"{self.title} timestamp:{self.timestamp}"
        self._create_table_sql = self._sql_saver.getCreateTableSql(self._table_name)
        self._insert_sql = self._sql_saver.getInsertSql(self._table_name)

        self._queueScript: Callable[[str], CoroutineType[Any, Any, None]]
        self._queueMany: Callable[[str, Any], CoroutineType[Any, Any, None]]
        self._task: asyncio.Task

        from ..workers.sqlite3 import SqlWorker

        self._queueScript, self._queueMany = SqlWorker.subscribe()

        # Create the table
        self._queueScript(self._create_table_sql)

        # Create the task that continuously submit queue request for registering frames
        self._task = asyncio.create_task(self.continuousSubmitFrames())

    def initialize(self):
        pass

    def getTableName(self):
        return self._table_name

    def getCreateTableSql(self):
        return self._create_table_sql

    def getInsertSql(self):
        return self._insert_sql

    def getConfig(self):
        return self._sql_saver.config.toDict()

    async def continuousSubmitFrames(self):
        while True:
            await asyncio.sleep(5)
            frames = self.toOwnedFrames()
            if frames:
                await self._queueMany(self._insert_sql, frames)

    # Memory for saving
    def toOwnedFrames(self):
        with self._frame_lock:
            frames = self.frames
            self.frames = []
            return frames

    # This would be called in the other thread
    def _save_fn(self, frame: Any):
        with self._frame_lock:
            self._frames.append(frame)
