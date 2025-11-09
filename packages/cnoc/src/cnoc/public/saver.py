import time
from typing import Any, Mapping, TypedDict, cast
import pandas as pd
from ._saver import Saver as _S
from ._utils import DataclassInstance


class Metadata(TypedDict):
    time: time.struct_time
    params: dict[str, Any]
    note: str


class Saver[T: Mapping[str, object]]:
    def __init__(self, path: str, params: DataclassInstance, type: type[T]):
        self._saver = _S[T](path, params, type)

    def save(self, data: T):
        self._saver.save(data)

    @property
    def saver(self):
        return self._saver


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
            cast(Metadata, store.get_storer(key).attrs.metadata),  # type: ignore
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
                cast(pd.DataFrame, store.get(key)),
                store.get_storer(key).attrs.metadata,  # type: ignore
            )
            for key in store.keys()
        ]
        store.close()
        return res

    def items(self):
        store = pd.HDFStore(self.path)
        res = {
            key: Reader.DataSet(
                cast(pd.DataFrame, store.get(key)),
                store.get_storer(key).attrs.metadata,  # type: ignore
            )
            for key in [key[1:] for key in store.keys()]
        }
        store.close()
        return res
