import asyncio

from threading import Lock
from typing import Any
from cnoc.extensions.saver import _SaverABC
from ..workers.sqlite import SqlWorker


class SaverProxy:
    def __init__(
        self,
        *,
        timestamp: int,
        saverT: type[_SaverABC],
        kwargs: Any,
    ):
        self._timestamp = timestamp
        # saver instance for consumer of saver
        self._saver = saverT(timestamp=self._timestamp, save_fn=self._save_fn, **kwargs)

        self._frames_lock = Lock()
        self._frames: list[Any] = []

        self._insert_sql = self._saver._insert_sql()

        self._should_cancel = asyncio.Event()
        self._stopped = asyncio.Event()

        # Create the table
        SqlWorker.putScript(self._saver._create_table_sql())

        # Create the task that continuously submit put request for registering frames
        self._task = asyncio.create_task(self._worker())

    """Public Interface"""

    def getConfig(self):
        return self._saver.config.toDict()

    async def finalize(self):
        self._should_cancel.set()
        await self._stopped.wait()
        return self._saver._finalize(
            await SqlWorker.putFetchall(self._saver._select_all_sql())
        )

    async def kill(self):
        # Cancel the task
        self._should_cancel.set()
        await self._stopped.wait()

    @property
    def title(self):
        return self._saver.config.title

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
        frames: list[Any]
        with self._frames_lock:
            frames = self._frames
            self._frames = []

        if frames:
            SqlWorker.putMany(self._insert_sql, frames)

    """_save_fn to be used by underlying saver"""

    def _save_fn(self, frame: Any):
        with self._frames_lock:
            self._frames.append(frame)
