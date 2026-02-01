import asyncio

import json
import os
from typing import Any, Callable, Coroutine, Mapping


from .saver import Saver


class Manager:
    def __init__(self, timestamp: int, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._tasks: list[asyncio.Task[Any]] = []
        self._savers: dict[str, Saver[Any]] = {}
        self._data_dir = f"./data/{timestamp}"
        os.makedirs(self._data_dir, exist_ok=True)

        # Set the expected loop count, -1 means infinite
        self.expected_loop_count = -1

    def createSaver[T: Mapping[str, object]](
        self, title: str, schema: type[T]
    ) -> Saver[T]:
        saver = Saver[T](self._data_dir, title, schema, self._run_coroutine_threadsafe)
        self._savers[title] = saver
        return saver

    """The value should be json serializable"""

    def saveMetadata(self, key: str, value: Any):
        if not os.path.exists(f"{self._data_dir}/metadata.json"):
            with open(f"{self._data_dir}/metadata.json", "w") as f:
                json.dump({key: value}, f)
            return

        with open(f"{self._data_dir}/metadata.json", "r") as f:
            metadata = json.load(f)
            metadata[key] = value

        with open(f"{self._data_dir}/metadata.json", "w") as f:
            json.dump(metadata, f)

    def _run_coroutine_threadsafe(self, coroutine: Coroutine[Any, Any, Any]) -> None:
        self._loop.call_soon_threadsafe(
            lambda: self._tasks.append(asyncio.create_task(coroutine))
        )

    def _call_soon_threadsafe(self, callback: Callable[[], None]) -> None:
        self._loop.call_soon_threadsafe(callback)

    async def _close(self) -> None:
        await asyncio.gather(*self._tasks)
        self._tasks = []
        for saver in self._savers.values():
            saver._saver.close()  # pyright: ignore[reportPrivateUsage]
