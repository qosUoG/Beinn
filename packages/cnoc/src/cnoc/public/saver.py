import json
import time
from typing import Any, Mapping, TypedDict, cast


import pandas as pd
from ._saver import Saver as _S
from ._utils import DataclassInstance
import pyarrow.parquet as pq


class Metadata(TypedDict):
    time: time.struct_time
    params: dict[str, Any]
    note: str


class Saver[T: Mapping[str, object]]:
    def __init__(self, path: str, params: DataclassInstance, type: type[T]):
        self._saver = _S[T](path, params, type)

    def save(self, data: T):
        self._saver.save(data)

    def saveMetadata(self, key: str, value: Any):
        self._saver.saveMetadata(key, value)

    @property
    def saver(self):
        return self._saver


class Reader:
    def __init__(self, path: str):
        self.data = pd.read_parquet(path)  # type: ignore
        self.time = int(pq.read_metadata(path).metadata[b"time"])  # type: ignore
        self.params = json.loads(pq.read_metadata(path).metadata[b"params"])  # type: ignore
        self.note = cast(str, pq.read_metadata(path).metadata[b"note"].decode())  # type: ignore
