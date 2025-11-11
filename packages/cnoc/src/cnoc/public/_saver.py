from datetime import datetime
import inspect
import json
from typing import Mapping, TypedDict
import pandas as pd
from ._utils import DataclassInstance
from ._params import AllParamSaveType, params2Save


class Metadata(TypedDict):
    time: int
    params: dict[str, AllParamSaveType | dict[str, AllParamSaveType]]
    note: str
    columns: list[str]


class Saver[T: Mapping[str, object]]:
    def __init__(self, path: str, params: DataclassInstance, type: type[T]):
        self._store = pd.HDFStore("data.h5")
        maximum = -1
        for key in self._store.keys():
            if not key.startswith(path):
                continue

            # Parse the number after the path
            maybe_number: int
            try:
                maybe_number = int(key.replace(path, ""))
            except ValueError:
                # If not a number, then it is not the same path
                continue

            maximum = max(maybe_number, maximum)
        self.path = f"{path}{maximum + 1}"

        self._metadata: Metadata = {
            "time": int(datetime.now().timestamp() * 1000),
            "params": params2Save(params),
            "note": "",
            "columns": list(tuple(inspect.get_annotations(type).keys())),
        }

    def save(self, data: T):
        if hasattr(self, "_attrs"):
            self._store.append(f"{self.path}", pd.DataFrame(data))
            return

        self._store.put(f"{self.path}", pd.DataFrame(data), format="table")
        self._attrs = self._store.get_storer(f"{self.path}").attrs  # type: ignore
        self._attrs.metadata = json.dumps(self._metadata)  # type: ignore

    def saveNote(self, note: str):
        if not hasattr(self, "_attrs"):
            self._attrs = self._store.get_storer(f"{self.path}").attrs  # type: ignore
        self._metadata["note"] = note
        self._attrs.metadata = json.dumps(self._metadata)  # type: ignore

    def close(self):
        self._store.close()
