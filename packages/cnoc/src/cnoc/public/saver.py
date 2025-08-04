import time
import pandas as pd


class Saver:
    def __init__(self, path: str):
        self.path = path
        self._store = pd.HDFStore(path)

        self._key = len(self._store.keys())
        self._setup_time = time.localtime()

        self._params: list[dict] = []

    def _cnoc_firstSave(self):
        self._attrs = self._store.get_storer(f"{self._key}").attrs
        self._attrs.time = self._setup_time
        self._attrs.params = self._params

    def _cnoc_saveParams(self, params: dict):
        self._params.append(params)
        if hasattr(self, "_attrs"):
            self._attrs.params = self._params

    def save(self, data: pd.DataFrame):
        if not hasattr(self, "_attrs"):
            self._store.put(f"{self._key}", data, format="table")
            self._cnoc_firstSave()

        else:
            self._store.append(f"{self._key}", data)

    def _cnoc_close(self):
        self._store.close()
