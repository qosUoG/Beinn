import asyncio
from threading import Event, Lock
import time
from typing import Any

from qoslablib.extensions.saver import SqlSaverABC

from ..workers.sqllite import SqlWorker


class SqlSaverProxy:
    def __init__(
        self,
        *,
        experiment_stopped: Event,
        experiment_success: Event,
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

        self._should_cancel = asyncio.Event()
        self._stopped = asyncio.Event()

        self._experiment_stopped = experiment_stopped
        self._experiment_success = experiment_success

        # Create the table
        SqlWorker.putScript(create_table_sql)

        # Create the task that continuously submit put request for registering frames
        self._task = asyncio.create_task(self._worker())

    """Public Interface"""

    def getConfig(self):
        return self._sql_saver.config.toDict()

    async def cleanup(self):
        # Cancel the task
        if not self._task.done():
            self._should_cancel.set()
            await self._stopped.wait()

    """Private task to continuously submit frames to worker"""

    async def _worker(self):
        while (
            not self._should_cancel.is_set()
            and not self._experiment_stopped.is_set()
            and not self._experiment_success.is_set()
        ):
            await asyncio.sleep(2)
            self._flushFrames()

        # flush the frames one last time
        self._flushFrames()
        self._stopped.set()

        if self._experiment_success.is_set():
            # TODO: fetch all data out and save to the sqlite db
            pass
        return

    def _flushFrames(self):
        frames = self._toOwnedFrames()
        if frames:
            SqlWorker.putMany(self._insert_sql, frames)

    def _toOwnedFrames(self):
        with self._frames_lock:
            frames = self._frames
            self._frames = []
            return frames

    """_save_fn to be used by underlying saver"""

    def _save_fn(self, frame: Any):
        with self._frames_lock:
            self._frames.append(frame)
