import time
from typing import TypedDict
import pandas as pd


class _Metadata(TypedDict):
    time: time.struct_time
    params: list[dict]


class Saver:
    def __init__(self, path: str):
        self.path = path
        self._store = pd.HDFStore(path)

        self._key = len(self._store.keys())

        self._metadata: _Metadata = {
            "time": time.localtime(),
            "params": [],
        }

    def _cnoc_saveParams(self, params: dict):
        self._metadata["params"].append(params)
        if hasattr(self, "_attrs"):
            self._attrs.metadata = self._metadata

    def save(self, data: pd.DataFrame):
        if hasattr(self, "_attrs"):
            self._store.append(f"{self._key}", data)
            return

        self._store.put(f"{self._key}", data, format="table")
        self._attrs = self._store.get_storer(f"{self._key}").attrs
        self._attrs.metadata = self._metadata

    def _cnoc_close(self):
        self._store.close()
