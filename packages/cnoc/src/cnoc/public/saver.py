import time
from typing import TypedDict
import pandas as pd

from ..public.params import Params, params2Save


class Saver:
    class _Metadata(TypedDict):
        time: time.struct_time
        params: dict
        note: str

    def __init__(self, path: str, params: Params):
        self.path = path
        self._store = pd.HDFStore(path)
        self._key = len(self._store.keys())

        self._metadata: Saver._Metadata = {
            "time": time.localtime(),
            "params": params2Save(params),
            "note": "",
        }

    def save(self, data: pd.DataFrame):
        if hasattr(self, "_attrs"):
            self._store.append(f"pid{self._key}", data)
            return

        self._store.put(f"pid{self._key}", data, format="table")
        self._attrs = self._store.get_storer(f"pid{self._key}").attrs
        self._attrs.metadata = self._metadata

    def saveNote(self, note: str):
        self._metadata["note"] = note

    def close(self):
        self._store.close()


class Reader:
    class DataSet:
        def __init__(self, data: pd.DataFrame, metadata: Saver._Metadata):
            self.data = data
            self.timestruct = metadata["time"]
            self.params = metadata["params"]
            self.note = metadata["note"]

        @property
        def time(self):
            return time.strftime("%Y/%m/%d %H:%M:%S UTC%z", self.timestruct)

    def __init__(self, path: str):
        self.path = path

    def get(self, key: str) -> DataSet:
        store = pd.HDFStore(self.path)
        dataset = Reader.DataSet(
            store.get(key),
            store.get_storer(key).attrs.metadata,
        )
        store.close()
        return dataset

    def keys(self):
        store = pd.HDFStore(self.path)
        keys = [key[1:] for key in store.keys()]
        store.close()
        return keys

    def values(self):
        store = pd.HDFStore(self.path)
        res = [
            Reader.DataSet(
                store.get(key),
                store.get_storer(key).attrs.metadata,
            )
            for key in store.keys()
        ]
        store.close()
        return res

    def items(self):
        store = pd.HDFStore(self.path)
        res = {
            key: Reader.DataSet(store.get(key), store.get_storer(key).attrs.metadata)
            for key in [key[1:] for key in store.keys()]
        }
        store.close()
        return res
