import time
from typing import TypedDict
import pandas as pd


class Saver:
    class _Metadata(TypedDict):
        time: time.struct_time
        params: list[dict]

    def __init__(self, path: str):
        self.path = path
        self._store = pd.HDFStore(path)

        self._key = len(self._store.keys())

        self._metadata: Saver._Metadata = {
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


class Reader:
    class DataSet:
        def __init__(self, data: pd.DataFrame, metadata: Saver._Metadata):
            self.data = data
            self.timestruct = metadata["time"]
            self.params = metadata["params"]

        @property
        def time(self):
            return time.strftime("%Y/%m/%d %H:%M:%S UTC%z", self.timestruct)

    @classmethod
    def read(cls, index: int, path: str):
        _store = pd.HDFStore(path)
        dataset = cls.DataSet(
            _store.get(f"{index}"),
            _store.get_storer(f"{index}").attrs.metadata,
        )
        _store.close()
        return dataset
