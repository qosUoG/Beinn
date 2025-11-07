import time
from typing import Any, TypedDict, cast
import pandas as pd

from ._params import Params
from ._saver import Saver as _S


class Metadata(TypedDict):
    time: time.struct_time
    params: dict[str, Any]
    note: str


class Saver:
    def __init__(self, path: str, params: Params):
        self._saver = _S(path, params)

    def save(self, data: pd.DataFrame):
        self._saver.save(data)


class Reader:
    class DataSet:
        def __init__(self, data: pd.DataFrame, metadata: Metadata):
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
            cast(pd.DataFrame, store.get(key)),
            cast(Metadata, store.get_storer(key).attrs.metadata),
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
