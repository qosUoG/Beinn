import time
from typing import TypedDict
import pandas as pd

from ._params import Params, params2Save


class Metadata(TypedDict):
    time: time.struct_time
    params: dict
    note: str


class Saver:
    def __init__(self, path: str, params: Params):
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
        self._attrs = self._store.get_storer(f"pid{self._key}").attrs
        self._attrs.metadata = self._metadata

    def saveNote(self, note: str):
        self._metadata["note"] = note

    def close(self):
        self._store.close()
