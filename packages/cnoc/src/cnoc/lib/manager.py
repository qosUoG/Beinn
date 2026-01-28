import asyncio
import json
import os
from typing import Any, Callable, Coroutine, Mapping

from ._utils import DataclassInstance

from .saver import Saver
from ._params import params2Save


class _Metadata:
    def __init__(self, dir: str, params: DataclassInstance):
        self._dir = dir
        self._params = params
        self._note = ""

        self._saveMetadata()

    @property
    def note(self) -> str:
        return self._note

    @note.setter
    def _(self, note: str):
        self._note = note
        self._saveMetadata()

    def _saveMetadata(self):
        with open(self._dir + "/" + "metadata.json", "w") as f:
            f.write(
                json.dumps(
                    {
                        "params": json.dumps(params2Save(self._params))
                        if self._params
                        else "{}",
                        "note": self._note,
                    }
                )
            )


class Manager:
    def __init__(
        self, timestamp: int, loop: asyncio.AbstractEventLoop, params: DataclassInstance
    ):
        self._loop = loop
        self._tasks: list[asyncio.Task[Any]] = []
        self._savers: dict[str, Saver[Any]] = {}
        self._data_dir = f"./data/{timestamp}"
        os.makedirs(self._data_dir, exist_ok=True)
        self._metadata: _Metadata = _Metadata(self._data_dir, params)
        # Set the expected loop count, -1 means infinite
        self.expected_loop_count = -1

    def createSaver[T: Mapping[str, object]](
        self, title: str, schema: type[T]
    ) -> Saver[T]:
        saver = Saver[T](self._data_dir, title, schema, self._run_coroutine_threadsafe)
        self._savers[title] = saver
        return saver

    def _run_coroutine_threadsafe(self, coroutine: Coroutine[Any, Any, Any]) -> None:
        self._loop.call_soon_threadsafe(
            lambda: self._tasks.append(asyncio.create_task(coroutine))
        )

    def _call_soon_threadsafe(self, callback: Callable[[], None]) -> None:
        self._loop.call_soon_threadsafe(callback)

    async def _wait_tasks(self) -> None:
        await asyncio.gather(*self._tasks)
        self._tasks = []

    def _close(self) -> None:
        for saver in self._savers.values():
            saver._saver.close()  # pyright: ignore[reportPrivateUsage]
