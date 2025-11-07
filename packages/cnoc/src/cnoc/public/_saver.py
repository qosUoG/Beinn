import time
from typing import TypedDict
import pandas as pd
from ._utils import DataclassInstance
from ._params import AllParamSaveType, params2Save


class Metadata(TypedDict):
    time: time.struct_time
    params: dict[str, AllParamSaveType | dict[str, AllParamSaveType]]
    note: str


class Saver:
    def __init__(self, path: str, params: DataclassInstance):
        self.path = path
        self._store = pd.HDFStore(path)
        self._key = len(self._store.keys())

        self._metadata: Metadata = {
            "time": time.localtime(),
            "params": params2Save(params),
            "note": "",
        }

    def save(self, data: pd.DataFrame):
        if hasattr(self, "_attrs"):
            self._store.append(f"pid{self._key}", data)
            return

        self._store.put(f"pid{self._key}", data, format="table")
        self._attrs = self._store.get_storer(f"pid{self._key}").attrs  # type: ignore
        self._attrs.metadata = self._metadata  # type: ignore

    def saveNote(self, note: str):
        if not hasattr(self, "_attrs"):
            self._attrs = self._store.get_storer(f"pid{self._key}").attrs  # type: ignore
        self._metadata["note"] = note
        self._attrs.metadata = self._metadata  # type: ignore

    def close(self):
        self._store.close()
